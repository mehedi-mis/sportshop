from django.urls import path
from .views import (
    ChatRoomListView, ChatRoomCreateView, ChatRoomDetailView, MessageCreateView
)


urlpatterns = [
    path('', ChatRoomListView.as_view(), name='chat_room_list'),
    path('create/', ChatRoomCreateView.as_view(), name='room_create'),
    path('<int:pk>/', ChatRoomDetailView.as_view(), name='chat_room_detail'),
    path('<int:pk>/send/', MessageCreateView.as_view(), name='message_create'),
]
