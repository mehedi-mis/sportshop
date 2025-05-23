from django.db import models
from users.models import CustomUser
from django.urls import reverse
from django.utils import timezone


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order', 'Order Update'),
        ('chat', 'New Message'),
        ('offer', 'Special Offer'),
        ('jersey', 'Custom Jersey Update'),
        ('system', 'System Notification'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.email}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def get_absolute_url(self):
        return self.related_url or reverse('notifications')