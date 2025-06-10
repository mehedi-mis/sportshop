from django.urls import path
from . import views
from .views import (
    TriviaListView, TriviaUpdateView,
    TriviaDeleteView, TriviaDetailView
)


urlpatterns = [
    path('', views.game_home, name='game_home'),
    path('play/', views.play_game, name='play_game'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    
    path('trivia/list/', TriviaListView.as_view(), name='trivia_list'),
    path('<int:pk>/', TriviaDetailView.as_view(), name='trivia_detail'),
    path('<int:pk>/edit/', TriviaUpdateView.as_view(), name='trivia_edit'),
    path('<int:pk>/delete/', TriviaDeleteView.as_view(), name='trivia_delete'),
    path('game/add/', views.create_game_question, name='create_game_question'),
]
