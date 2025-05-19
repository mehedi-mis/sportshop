from datetime import datetime

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderItem
from .forms import OrderForm, OrderStatusForm
from cart.utils import SessionCart


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


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_create.html'
    success_url = reverse_lazy('order_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = SessionCart(self.request)
        context['cart'] = cart
        context['cart_items'] = list(cart.__iter__())
        return context

    def form_valid(self, form):
        cart = SessionCart(self.request)
        if len(cart) == 0:
            messages.error(self.request, "Your cart is empty")
            return redirect('cart_detail')

        order = form.save(commit=False)
        order.user = self.request.user
        order.order_total = cart.get_total_price()
        order.save()

        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )

        # Clear the cart
        cart.clear()

        # Send confirmation email
        self.send_order_confirmation_email(order)

        messages.success(self.request, "Your order has been placed successfully!")
        return redirect('order_detail', pk=order.pk)

    def send_order_confirmation_email(self, order):
        subject = f"Order Confirmation - #{order.order_number}"
        message = f"Thank you for your order!\n\nOrder Number: {order.order_number}\nTotal: ${order.order_total}"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )


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
