from django.db import models
from users.models import CustomUser
from chat.models import ChatRoom
from products.models import Product


class CustomJerseyOrder(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending Approval'),
        ('A', 'Approved'),
        ('D', 'In Design'),
        ('PR', 'In Production'),
        ('S', 'Shipped'),
        ('C', 'Completed'),
        ('R', 'Rejected'),
    ]

    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    name_on_jersey = models.CharField(max_length=100)
    jersey_number = models.PositiveIntegerField()
    size = models.CharField(max_length=5, choices=Product.SIZE_CHOICES)
    primary_color = models.CharField(max_length=50)
    secondary_color = models.CharField(max_length=50, blank=True)
    team_logo = models.ImageField(upload_to='custom_jerseys/logos/', blank=True)
    design_preferences = models.TextField(blank=True)
    reference_image = models.ImageField(upload_to='custom_jerseys/references/', blank=True)
    reference_image_back = models.ImageField(upload_to='custom_jerseys/references/', blank=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='P')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Custom Jersey Order #{self.order_number}"
