from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

from .views import UserListView, UserUpdateView, UserDeleteView

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('profile/', views.profile_view, name='profile'),

    path('users/', UserListView.as_view(), name='users_list'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='users_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='users_delete'),

    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='account/password_change.html',
        success_url=reverse_lazy('profile')
    ), name='password_change'),
    path('profile/edit/', views.update_profile, name='update_profile'),
]
