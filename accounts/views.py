from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm, UserPasswordChangeForm


def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful, welcome!')
            return redirect('blog:post_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'blog:post_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('blog:post_list')


@login_required
def account_settings(request):
    """Allow logged-in user to edit own username/email and password."""
    user = request.user
    if request.method == 'POST':
        if 'profile_submit' in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            password_form = UserPasswordChangeForm(user=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('accounts:settings')
        elif 'password_submit' in request.POST:
            profile_form = ProfileForm(instance=user)
            password_form = UserPasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('accounts:settings')
    else:
        profile_form = ProfileForm(instance=user)
        password_form = UserPasswordChangeForm(user=user)

    return render(
        request,
        'accounts/settings.html',
        {
            'profile_form': profile_form,
            'password_form': password_form,
        },
    )
