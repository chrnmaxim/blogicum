"""Module of blog app configuration."""
from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Configuration class of blog app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Блог'
