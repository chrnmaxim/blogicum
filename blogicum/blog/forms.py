"""Forms for blog app."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    """Post creation form."""

    class Meta():
        model = Post
        exclude = ('author', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CustomUserCreationForm(UserCreationForm):
    """
    User creation form.

    Ads fields first_name, last_name and  email.
    """

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class UserEditForm(forms.ModelForm):
    """Edit user data form without password."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):
    """Comment add form."""

    class Meta:
        model = Comment
        fields = ('text',)
