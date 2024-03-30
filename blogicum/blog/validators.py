"""Custom validators for blog app."""

from django.core.exceptions import ValidationError
from django.utils import timezone

TIME_DELTA: int = 10


def post_pub_date(pub_date: timezone) -> None:
    """Validate post pub_date."""
    formatted_pub_date = pub_date.strftime("%Y-%m-%d")
    formatted_local_time = (
        timezone.localtime() - timezone.timedelta(minutes=10)
    ).strftime("%Y-%m-%d")
    if formatted_pub_date < formatted_local_time:
        raise ValidationError(
            f'Дата публикации {formatted_pub_date} не может быть раньше, '
            f'чем {formatted_local_time}.'
        )


def is_profanity(text: str) -> None:
    """Validate profanity in Post text."""
    from .models import Profanity
    profanity_list = list(Profanity.objects.values_list('word', flat=True))
    words = text.replace(',', ' ').lower().split()
    if any(word in words for word in profanity_list):
        raise ValidationError(
            'Пожалуйста, не используйте обсценную лексику.'
        )
