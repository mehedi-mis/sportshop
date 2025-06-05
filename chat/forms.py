from django import forms
from django.db.models import Subquery
from .models import ChatRoom, Message
from users.models import CustomUser


class ChatRoomForm(forms.ModelForm):
    admin = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(
            is_staff=True
        ),
        label="Select Admin"
    )

    class Meta:
        model = ChatRoom
        fields = ['admin']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'}),
        }
