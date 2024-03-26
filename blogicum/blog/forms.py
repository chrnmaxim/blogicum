from django import forms

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta():
        model = Post
        exclude = ('author', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
