from datetime import datetime
from django.utils import timezone
from decimal import Decimal
import stripe
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderItem
from .forms import OrderForm, OrderStatusForm
from cart.utils import SessionCart
from website.models import SiteConfiguration
from leaderboard.models import UserDiscount

stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


class OrderStatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    form_class = OrderStatusForm
    template_name = 'orders/order_status_update.html'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        order = form.save()
        if order.status == 'D' and not order.delivered_at:
            order.delivered_at = datetime.now()
            order.save()
        messages.success(self.request, f"Order #{order.order_number} status updated to {order.get_status_display()}")
        return redirect('order_detail', pk=order.pk)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_create.html'
    success_url = reverse_lazy('order_list')

    site_config_obj = SiteConfiguration.objects.first()
    shipping_cost = site_config_obj.shipping_cost if site_config_obj else 0.0
    tax_cost = site_config_obj.tax_percentage if site_config_obj else 0.0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = SessionCart(self.request)
        context['cart'] = cart
        context['cart_items'] = list(cart.__iter__())
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['stripe_amount'] = int(cart.get_total_price() + self.shipping_cost)
        context['shipping_cost'] = self.shipping_cost
        return context

    def form_valid(self, form):
        now = timezone.now()
        has_discount = UserDiscount.objects.filter(
            user=self.request.user,
            expires_at__gte=now,
            is_used=False
        )

        cart = SessionCart(self.request)
        if len(cart) == 0:
            messages.error(self.request, "Your cart is empty")
            return redirect('cart_detail')

        order = form.save(commit=False)
        order.user = self.request.user
        if has_discount.exists() and has_discount.first().discount_code == form.cleaned_data.get('coupon_code'):
            order.order_total = cart.get_total_price() - has_discount.first().discount_percentage
        else:
            order.order_total = cart.get_total_price()
        order.shipping_cost = self.shipping_cost
        order.tax = self.tax_cost
        order.save()

        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
        if order.payment_method == 'STRIPE':
            return self.stripe_checkout(cart, order)
        else:
            order.status = 'P'
            order.save()
            # create cart session
            cart.clear()
            messages.success(self.request, "Order created successfully")
            return redirect('order_detail', pk=order.pk)

    def stripe_checkout(self, cart, order):
        # Redirect to Stripe checkout session
        stripe.api_key = settings.STRIPE_SECRET_KEY

        line_items = [
            {
                'price_data': {
                    'currency': 'BDT',
                    'product_data': {
                        'name': item['product'].name,
                    },
                    'unit_amount': int(item['price'] * 100),  # Stripe uses cents
                },
                'quantity': item['quantity'],
            } for item in cart
        ]

        # Add shipping cost as a separate line item
        line_items.append({
            'price_data': {
                'currency': 'BDT',
                'product_data': {
                    'name': 'Shipping Cost',
                },
                'unit_amount': int(self.shipping_cost * 100),
            },
            'quantity': 1,
        })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=self.request.build_absolute_uri(
                reverse_lazy('payment_success')) + f'?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=self.request.build_absolute_uri(reverse_lazy('payment_cancelled')),
            metadata={'order_id': order.id}
        )

        return redirect(checkout_session.url)


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/payment_success.html'

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if session_id:
            try:
                # Retrieve the Stripe session
                session = stripe.checkout.Session.retrieve(session_id)

                # Get the order from metadata
                order = Order.objects.get(
                    id=session.metadata.order_id,
                    user=request.user
                )

                # Mark as paid
                order.mark_as_paid()

                # Clear the cart
                SessionCart(request).clear()

                # Clear the session order ID
                if 'current_order_id' in request.session:
                    del request.session['current_order_id']

                return render(request, self.template_name, {'order': order})

            except Exception as e:
                messages.error(request, str(e))
                return redirect('order_list')
        messages.success(self.request, "Your order is not valid!")
        return redirect('order_list')


class PaymentCancelledView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/payment_cancelled.html'
