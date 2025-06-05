from chat.models import ChatRoom
from django.shortcuts import redirect


def get_chat_room(request):
    if request.user.is_authenticated:
        return {'chat_room_id': ChatRoom.objects.filter(user=request.user).first()}
    return {}
