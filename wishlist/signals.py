from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import Wishlist


@receiver(post_save, sender=CustomUser)
def create_user_wishlist(sender, instance, created, **kwargs):
    if created:
        Wishlist.objects.create(user=instance)
