from django import forms
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


class ChatRoomForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=False),
        label="Select User"
    )

    class Meta:
        model = ChatRoom
        fields = ['user']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'}),
        }
