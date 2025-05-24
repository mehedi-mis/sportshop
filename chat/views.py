from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ChatRoom, Message
from .forms import MessageForm,ChatRoomForm


class ChatRoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chat/room_list.html'
    context_object_name = 'chat_rooms'

    def get_queryset(self):
        if self.request.user.is_staff:
            return ChatRoom.objects.filter(admin=self.request.user)
        return ChatRoom.objects.filter(user=self.request.user)


class ChatRoomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ChatRoom
    form_class = ChatRoomForm
    template_name = 'chat/room_create.html'
    success_url = reverse_lazy('chat_room_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.admin = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Chat room created with {form.instance.user.email}")
        return response


class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'chat/room_detail.html'
    context_object_name = 'chat_room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MessageForm()
        context['chat_messages'] = self.object.messages.all().order_by('created_at')
        return context

    def get_queryset(self):
        if self.request.user.is_staff:
            return ChatRoom.objects.filter(admin=self.request.user)
        return ChatRoom.objects.filter(user=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'chat/message_form.html'

    def form_valid(self, form):
        chat_room = get_object_or_404(ChatRoom, pk=self.kwargs['pk'])
        if self.request.user not in [chat_room.user, chat_room.admin]:
            messages.error(self.request, "You don't have permission to send messages in this chat")
            return redirect('chat_room_list')

        message = form.save(commit=False)
        message.chat_room = chat_room
        message.sender = self.request.user

        # Mark as read if sender is admin
        if self.request.user == chat_room.admin:
            message.is_read = True

        message.save()
        return redirect('chat_room_detail', pk=chat_room.pk)
