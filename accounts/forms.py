from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import Profile


class RegisterForm(UserCreationForm):
    """User registration form"""
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Username',
        }


class LoginForm(AuthenticationForm):
    """User login form"""
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, label='Avatar')

    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': 'Username',
            'email': 'Email',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if self.user:
            profile, _ = Profile.objects.get_or_create(user=self.user)
            self.fields['avatar'].initial = profile.avatar

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, _ = Profile.objects.get_or_create(user=user)
        avatar_file = self.cleaned_data.get('avatar')
        if avatar_file:
            profile.avatar = avatar_file
            profile.save()

        return user


class UserPasswordChangeForm(PasswordChangeForm):
    """Wrapper around Django's PasswordChangeForm (rules are in settings)."""
    old_password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput,
    )
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput,
    )
