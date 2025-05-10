from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .models import CustomUser
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .tokens import account_activation_token
import random
import string


def register_view(request):
    """Email Sign Up Views"""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User inactive until email verification
            user.save()

            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Activate your Sports Shop account'
            message = render_to_string('users/email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=message
            )

            messages.success(request, 'Please confirm your email address to complete registration')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Your account has been verified successfully! You can now login.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or has expired!')
        return redirect('register')


def login_view(request):
    """Email Login Views"""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserLoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                    next_url = request.GET.get('next', 'profile')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Account is not active. Please verify your email first.')
            else:
                messages.error(request, 'Invalid email or password')
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Logout View"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# Google Authentication Views (using allauth)
# These are handled by django-allauth, just need proper configuration

@login_required
def profile_view(request):
    """Profile View with update functionality"""
    user = request.user
    profile_updated = False

    if request.method == 'POST':
        # Initialize form with current user data and POST data
        form = UserProfileForm(request.POST, request.FILES or None, instance=user)

        if form.is_valid():
            # Handle profile picture upload separately
            if 'profile_picture' in request.FILES:
                # Delete old profile picture if it exists
                if user.profile_picture:
                    user.profile_picture.delete(save=False)
                # Save new profile picture
                user.profile_picture = form.cleaned_data['profile_picture']

            # Save the form data
            form.save()
            profile_updated = True
            messages.success(request, 'Your profile has been updated successfully!')

            # Redirect to prevent form resubmission
            return redirect('profile')
    else:
        # Initialize form with current user data
        form = UserProfileForm(instance=user)

    context = {
        'form': form,
        'profile_updated': profile_updated,
        'user': user
    }
    return render(request, 'users/profile.html', context)
