from django.db.models.signals import pre_save
from django.dispatch import receiver
import uuid
from .models import Order


@receiver(pre_save, sender=Order)
def generate_order_number(sender, instance, **kwargs):
    if not instance.order_number:
        instance.order_number = uuid.uuid4().hex[:10].upper()
