import uuid

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from chat.models import ChatRoom, Message
from .models import CustomJerseyOrder
from .forms import CustomJerseyOrderForm, CustomJerseyStatusForm


class CustomJerseyOrderListView(LoginRequiredMixin, ListView):
    model = CustomJerseyOrder
    template_name = 'custom_jerseys/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomJerseyOrder.objects.all().order_by('-created_at')
        return CustomJerseyOrder.objects.filter(user=self.request.user).order_by('-created_at')


class CustomJerseyOrderDetailView(LoginRequiredMixin, DetailView):
    model = CustomJerseyOrder
    template_name = 'custom_jerseys/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomJerseyOrder.objects.all()
        return CustomJerseyOrder.objects.filter(user=self.request.user)


class CustomJerseyOrderCreateView(LoginRequiredMixin, CreateView):
    model = CustomJerseyOrder
    form_class = CustomJerseyOrderForm
    template_name = 'custom_jerseys/order_create.html'

    def get_success_url(self):
        return reverse('custom_jersey_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        chat_room = get_object_or_404(ChatRoom, pk=self.kwargs['pk'], user=self.request.user)

        order = form.save(commit=False)
        order.chat_room = chat_room
        order.user = self.request.user
        order.order_number = self.generate_order_number()
        order.save()

        # Create a message in the chat room
        message_content = f"""New Custom Jersey Order Request:
- Name: {order.name_on_jersey}
- Number: {order.jersey_number}
- Size: {order.get_size_display()}
- Colors: {order.primary_color} / {order.secondary_color or 'None'}"""

        Message.objects.create(
            chat_room=chat_room,
            sender=self.request.user,
            content=message_content
        )

        messages.success(self.request, "Your custom jersey order has been submitted!")
        return redirect('custom_jersey_detail', pk=order.pk)

    def generate_order_number(self):
        return f"CJ-{uuid.uuid4().hex[:8].upper()}"


class CustomJerseyStatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomJerseyOrder
    form_class = CustomJerseyStatusForm
    template_name = 'custom_jerseys/status_update.html'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        order = form.save()
        self.send_status_update_email(order)
        messages.success(self.request, f"Order #{order.order_number} status updated to {order.get_status_display()}")
        return redirect('custom_jersey_detail', pk=order.pk)

    def send_status_update_email(self, order):
        subject = f"Custom Jersey Order Update - #{order.order_number}"
        message = f"""Your custom jersey order status has been updated:

Order Number: {order.order_number}
New Status: {order.get_status_display()}

Current Price: ${order.price}"""
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )