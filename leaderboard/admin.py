# game/admin.py
from django.contrib import admin
from django.utils import timezone
from django.db.models import Count, Sum
from django.http import HttpResponse
import csv
from .models import TriviaQuestion, UserScore, LeaderboardPrize, UserDiscount


class TriviaQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'sport', 'difficulty', 'correct_answer', 'is_active', 'created_at')
    list_filter = ('sport', 'difficulty', 'is_active', 'created_at')
    search_fields = ('question', 'explanation')
    list_editable = ('is_active',)
    actions = ['export_questions']

    def export_questions(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="trivia_questions.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Question', 'Sport', 'Difficulty', 'Option 1', 'Option 2',
            'Option 3', 'Option 4', 'Correct Answer', 'Explanation'
        ])

        for question in queryset:
            writer.writerow([
                question.question,
                question.get_sport_display(),
                question.get_difficulty_display(),
                question.option1,
                question.option2,
                question.option3,
                question.option4,
                question.correct_answer,
                question.explanation,
            ])

        return response

    export_questions.short_description = "Export selected questions to CSV"


class UserScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'correct_answers', 'wrong_answers', 'month', 'year', 'accuracy')
    list_filter = ('month', 'year', 'user')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_played',)

    def accuracy(self, obj):
        total = obj.correct_answers + obj.wrong_answers
        return f"{(obj.correct_answers / total * 100):.1f}%" if total > 0 else "N/A"

    accuracy.short_description = "Accuracy"

    actions = ['award_discounts', 'export_scores']

    def award_discounts(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        import uuid

        count = 0
        for score in queryset:
            # Check if user already has an active discount
            existing = UserDiscount.objects.filter(
                user=score.user,
                expires_at__gte=timezone.now(),
                is_used=False
            ).exists()

            if not existing:
                discount_code = f"TRIVIA-{score.user.username[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
                UserDiscount.objects.create(
                    user=score.user,
                    discount_code=discount_code,
                    discount_percentage=50,
                    expires_at=timezone.now() + timedelta(days=30)
                )
                count += 1

        self.message_user(request, f"Successfully awarded discounts to {count} users.")

    award_discounts.short_description = "Award 50% discount to selected users"

    def export_scores(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_scores.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Username', 'Email', 'Month', 'Year', 'Score',
            'Correct Answers', 'Wrong Answers', 'Accuracy'
        ])

        for score in queryset:
            total = score.correct_answers + score.wrong_answers
            accuracy = f"{(score.correct_answers / total * 100):.1f}%" if total > 0 else "N/A"

            writer.writerow([
                score.user.username,
                score.user.email,
                score.month,
                score.year,
                score.score,
                score.correct_answers,
                score.wrong_answers,
                accuracy,
            ])

        return response

    export_scores.short_description = "Export selected scores to CSV"


class LeaderboardPrizeAdmin(admin.ModelAdmin):
    list_display = ('month_year', 'prize_type', 'prize_value', 'is_active')
    list_filter = ('is_active', 'prize_type')
    list_editable = ('is_active',)

    def month_year(self, obj):
        return f"{obj.month}/{obj.year}"

    month_year.short_description = "Month/Year"
    month_year.admin_order_field = 'year'


class UserDiscountAdmin(admin.ModelAdmin):
    list_display = ('user', 'discount_code', 'discount_percentage', 'is_used', 'expires_at', 'is_valid')
    list_filter = ('is_used', 'discount_percentage')
    search_fields = ('user__username', 'discount_code')
    readonly_fields = ('created_at',)

    def is_valid(self, obj):
        return obj.is_valid()

    is_valid.boolean = True
    is_valid.short_description = "Valid"


admin.site.register(TriviaQuestion, TriviaQuestionAdmin)
admin.site.register(UserScore, UserScoreAdmin)
admin.site.register(LeaderboardPrize, LeaderboardPrizeAdmin)
admin.site.register(UserDiscount, UserDiscountAdmin)