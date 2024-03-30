"""Forms for blog app."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    """Post creation form."""

    class Meta:
        """Inner Meta class of Post creation form."""

        model = Post
        exclude = ('author', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format=('%Y-%m-%dT%H:%M'), attrs={'type': 'datetime-local'}
            )
        }


class CustomUserCreationForm(UserCreationForm):
    """
    User creation form.

    Ads fields first_name, last_name and  email.
    """

    class Meta:
        """Inner Meta class of User creation form."""

        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class UserEditForm(forms.ModelForm):
    """Edit user data form without password."""

    class Meta:
        """Inner Meta class of User data edit form."""

        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):
    """Comment add form."""

    class Meta:
        """Inner Meta class of Comment add form."""

        model = Comment
        fields = ('text',)
