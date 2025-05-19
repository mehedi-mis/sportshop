from django.db import models
from users.models import CustomUser


class ChatRoom(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admin_chats')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'admin')

    def __str__(self):
        return f"Chat between {self.user.email} and admin"


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='chat_images/', blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"
