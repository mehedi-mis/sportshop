from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from .models import TriviaQuestion, UserScore, LeaderboardPrize, UserDiscount
from products.models import Product
import random
import uuid
from datetime import timedelta


@login_required
def game_home(request):
    now = timezone.now()
    leaderboard = UserScore.get_current_leaderboard()
    current_prize = LeaderboardPrize.get_current_prize()

    user_score = UserScore.objects.filter(
        user=request.user,
        month=now.month,
        year=now.year
    ).first()

    # Check if user is in top 5 and hasn't received discount yet
    has_discount = False
    if user_score and leaderboard:
        is_in_top5 = user_score in [entry for entry in leaderboard]
        if is_in_top5:
            has_discount = UserDiscount.objects.filter(
                user=request.user,
                expires_at__gte=now,
                is_used=False
            ).exists()

    context = {
        'leaderboard': leaderboard,
        'user_score': user_score,
        'current_prize': current_prize,
        'has_discount': has_discount,
    }
    return render(request, 'game/game_home.html', context)


@login_required
def play_game(request):
    # Check if user has played too many times today (optional limit)
    today = timezone.now().date()
    questions_today = request.user.game_scores.filter(
        last_played__date=today
    ).count()

    if questions_today >= 20:  # Limit to 20 questions per day
        messages.info(request, "You've reached your daily play limit. Come back tomorrow!")
        return redirect('game_home')

    # Get all active questions
    questions = TriviaQuestion.objects.filter(is_active=True)

    # If you want to avoid repeating questions, you'll need to track which questions
    # the user has already answered. You could either:
    # 1. Create a separate model to track answered questions, or
    # 2. Use session storage to track recently shown questions

    # Option 2: Using session (simpler implementation)
    if 'recent_questions' not in request.session:
        request.session['recent_questions'] = []

    # Exclude recently shown questions (last 5 questions)
    recent_question_ids = request.session['recent_questions']
    available_questions = questions.exclude(id__in=recent_question_ids)

    # If no questions available, reset the recent questions list
    if not available_questions.exists():
        available_questions = questions
        request.session['recent_questions'] = []
        # Check if there are ANY questions available at all
        messages.error(request, "No questions are available at the moment. Please check back later.")
        return redirect('game_home')

    # Convert queryset to list for random.choice
    questions_list = list(available_questions)
    question = random.choice(questions_list)

    # Select random question
    # question = random.choice(available_questions)


    # Update recent questions in session (keep only last 5)
    recent_question_ids.append(question.id)
    request.session['recent_questions'] = recent_question_ids[-5:]
    request.session.modified = True

    context = {
        'question': question,
        'options': [
            question.option1,
            question.option2,
            question.option3,
            question.option4,
        ]
    }
    return render(request, 'game/play.html', context)


@login_required
@transaction.atomic
def submit_answer(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        question_id = request.POST.get('question_id')
        answer = request.POST.get('answer')

        try:
            question = TriviaQuestion.objects.get(id=question_id)
            is_correct = int(answer) == question.correct_answer

            # Update user score
            now = timezone.now()
            user_score, created = UserScore.objects.get_or_create(
                user=request.user,
                month=now.month,
                year=now.year,
                defaults={'score': 0, 'correct_answers': 0, 'wrong_answers': 0}
            )

            if is_correct:
                # Award points based on difficulty
                points = {
                    'E': 10,
                    'M': 20,
                    'H': 30
                }.get(question.difficulty, 10)

                user_score.score += points
                user_score.correct_answers += 1
            else:
                user_score.wrong_answers += 1

            user_score.save()

            # Check if user entered top 5 and award discount if needed
            award_discount_if_eligible(request.user)

            return JsonResponse({
                'correct': is_correct,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'points_earned': points if is_correct else 0,
                'total_score': user_score.score,
                'leaderboard_position': get_leaderboard_position(user_score),
                'in_top5': is_in_top5(user_score)
            })

        except (TriviaQuestion.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Invalid request'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def award_discount_if_eligible(user):
    now = timezone.now()
    user_score = UserScore.objects.filter(
        user=user,
        month=now.month,
        year=now.year
    ).first()

    if not user_score:
        return False

    leaderboard = UserScore.get_current_leaderboard()
    if not leaderboard:
        return False

    # Check if user is in top 5
    is_in_top5 = user_score in [entry for entry in leaderboard]
    if not is_in_top5:
        return False

    # Check if user already has an unused discount
    existing_discount = UserDiscount.objects.filter(
        user=user,
        expires_at__gte=now,
        is_used=False
    ).exists()

    if existing_discount:
        return False

    # Create new discount
    discount_code = f"TRIVIA-{user.username[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
    expires_at = now + timedelta(days=30)  # Valid for 30 days

    UserDiscount.objects.create(
        user=user,
        discount_code=discount_code,
        discount_percentage=50,
        expires_at=expires_at
    )

    return True


def is_in_top5(user_score):
    leaderboard = UserScore.get_current_leaderboard()
    return user_score in [entry for entry in leaderboard]


def get_leaderboard_position(user_score):
    leaderboard = UserScore.get_current_leaderboard()
    try:
        return list(leaderboard).index(user_score) + 1
    except ValueError:
        return None