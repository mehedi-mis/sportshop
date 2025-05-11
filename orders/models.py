from django.db import models
from django.utils import timezone
from users.models import CustomUser
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('PR', 'Processing'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('C', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('CC', 'Credit Card'),
        ('PP', 'PayPal'),
        ('STRIPE', 'Stripe'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='P')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number

    def get_total_with_shipping(self):
        return self.order_total + self.shipping_cost + self.tax

    def mark_as_paid(self):
        self.is_paid = True
        self.paid_at = timezone.now()
        self.save()

    def can_be_cancelled(self):
        return self.status in ['P', 'PR']

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for order {self.order.order_number}"

    def get_cost(self):
        return self.price * self.quantity
