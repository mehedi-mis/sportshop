from django.db import models
from users.models import CustomUser
from django.utils import timezone
from products.models import Product


class TriviaQuestion(models.Model):
    SPORT_CHOICES = [
        ('FB', 'Football'),
        ('BB', 'Basketball'),
        ('TN', 'Tennis'),
        ('BS', 'Baseball'),
        ('SK', 'Soccer'),
        ('OT', 'Other'),
    ]

    DIFFICULTY_CHOICES = [
        ('E', 'Easy'),
        ('M', 'Medium'),
        ('H', 'Hard'),
    ]

    question = models.TextField()
    sport = models.CharField(max_length=2, choices=SPORT_CHOICES)
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_answer = models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)])
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_sport_display()} - {self.question[:50]}..."

    class Meta:
        ordering = ['-created_at']


class UserScore(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='game_scores')
    score = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    month = models.PositiveSmallIntegerField()  # 1-12
    year = models.PositiveSmallIntegerField()
    last_played = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'month', 'year')
        ordering = ['-year', '-month', '-score']

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}: {self.score} pts"

    @classmethod
    def get_current_leaderboard(cls):
        now = timezone.now()
        return cls.objects.filter(
            month=now.month,
            year=now.year
        ).order_by('-score')[:5]


class LeaderboardPrize(models.Model):
    PRIZE_TYPE_CHOICES = [
        ('DISCOUNT', 'Percentage Discount'),
        ('PRODUCT', 'Free Product'),
        ('COUPON', 'Special Coupon'),
    ]

    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    prize_type = models.CharField(max_length=10, choices=PRIZE_TYPE_CHOICES)
    prize_value = models.CharField(max_length=100, help_text="Discount percentage, product ID, or coupon code")
    prize_description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('month', 'year')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.get_prize_type_display()} for {self.month}/{self.year}"

    @classmethod
    def get_current_prize(cls):
        now = timezone.now()
        return cls.objects.filter(
            month=now.month,
            year=now.year,
            is_active=True
        ).first()


class UserDiscount(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='game_discounts')
    discount_code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.PositiveIntegerField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.discount_code} - {self.discount_percentage}% for {self.user.username}"

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at