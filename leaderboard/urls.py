from django.urls import path
from . import views


urlpatterns = [
    path('', views.game_home, name='game_home'),
    path('play/', views.play_game, name='play_game'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
]
