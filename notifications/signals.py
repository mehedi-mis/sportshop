from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from orders.models import Order
from chat.models import Message
from custom_jerseys.models import CustomJerseyOrder
from notifications.models import Notification


@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type='order',
            title=f"Order #{instance.order_number} Placed",
            message=f"Your order #{instance.order_number} has been received and is being processed.",
            related_url=reverse('order_detail', args=[instance.pk])
        )
    else:
        if instance.status == 'S':
            Notification.objects.create(
                user=instance.user,
                notification_type='order',
                title=f"Order #{instance.order_number} Shipped",
                message=f"Your order #{instance.order_number} has been shipped.",
                related_url=reverse('order_detail', args=[instance.pk])
            )
        elif instance.status == 'D':
            Notification.objects.create(
                user=instance.user,
                notification_type='order',
                title=f"Order #{instance.order_number} Delivered",
                message=f"Your order #{instance.order_number} has been delivered.",
                related_url=reverse('order_detail', args=[instance.pk])
            )


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created and instance.sender != instance.chat_room.user:
        Notification.objects.create(
            user=instance.chat_room.user,
            notification_type='chat',
            title="New Message Received",
            message=f"You have a new message in your chat with admin.",
            related_url=reverse('chat_room_detail', args=[instance.chat_room.pk])
        )


@receiver(post_save, sender=CustomJerseyOrder)
def create_jersey_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type='jersey',
            title="Custom Jersey Order Submitted",
            message=f"Your custom jersey order #{instance.order_number} has been received.",
            related_url=reverse('custom_jersey_detail', args=[instance.pk])
        )
    else:
        if instance.status == 'A':
            Notification.objects.create(
                user=instance.user,
                notification_type='jersey',
                title=f"Custom Jersey Approved",
                message=f"Your custom jersey order #{instance.order_number} has been approved.",
                related_url=reverse('custom_jersey_detail', args=[instance.pk])
            )
        elif instance.status == 'S':
            Notification.objects.create(
                user=instance.user,
                notification_type='jersey',
                title=f"Custom Jersey Shipped",
                message=f"Your custom jersey order #{instance.order_number} has been shipped.",
                related_url=reverse('custom_jersey_detail', args=[instance.pk])
            )
