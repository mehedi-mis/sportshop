from django.urls import path
from .views import NotificationListView, mark_as_read, mark_all_as_read, unread_notifications_count


urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications'),
    path('<int:pk>/read/', mark_as_read, name='notification_read'),
    path('read-all/', mark_all_as_read, name='notifications_read_all'),
    path('unread-count/', unread_notifications_count, name='notifications_unread_count'),
]