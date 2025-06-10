from chat.models import ChatRoom
from django.shortcuts import redirect


def get_chat_room(request):
    if request.user.is_authenticated and ChatRoom.objects.filter(user=request.user).exists():
        return {'chat_room_id': ChatRoom.objects.filter(user=request.user).first()}
    return {'chat_room_id': None}
