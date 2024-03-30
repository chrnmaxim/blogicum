"""Models of blog app."""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from .validators import is_profanity, post_pub_date

CHARS_LIMIT: int = 30

MAX_LENGTH: int = 256

User = get_user_model()


class PublishedModel(models.Model):
    """Abstract model. Adds is_published and created_at flags."""

    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True
    )

    class Meta:
        """Inner Meta class of Abstract model."""

        abstract = True


class Category(PublishedModel):
    """Model for category data."""

    title = models.CharField(
        'Заголовок',
        max_length=MAX_LENGTH
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, '
            'дефис и подчёркивание.'
        )
    )

    class Meta:
        """Inner Meta class of Category model."""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        """Display category title in admin panel."""
        return self.title[:CHARS_LIMIT]


class Location(PublishedModel):
    """Model for location data."""

    name = models.CharField(
        verbose_name='Название места',
        max_length=MAX_LENGTH
    )

    class Meta:
        """Inner Meta class of Location model."""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        """Display location name in admin panel."""
        return self.name[:CHARS_LIMIT]


class Post(PublishedModel):
    """Model for post data."""

    title = models.CharField(
        verbose_name='Заголовок',
        max_length=MAX_LENGTH,
        validators=(is_profanity,)
    )
    text = models.TextField(
        verbose_name='Текст',
        validators=(is_profanity,)
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
        default=timezone.now,
        validators=(post_pub_date,)
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
        null=True

    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True
    )
    image = models.ImageField(
        'Изображение',
        upload_to='post_images',
        blank=True
    )

    class Meta:
        """Inner Meta class of Location model."""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        """Display Post title in admin panel."""
        return self.title[:CHARS_LIMIT]


class Comment(PublishedModel):
    """Model for comments data."""

    text = models.TextField(
        'Текст комментария',
        validators=(is_profanity,)
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Публикация',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        """Inner Meta class of Comment model."""

        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self) -> str:
        """Display Comment text in admin panel."""
        return self.text[:CHARS_LIMIT]


class Profanity(models.Model):
    """Model for add profanity."""

    word = models.TextField('Слово')

    class Meta:
        """Inner Meta class of Comment model."""

        verbose_name = 'слово'
        verbose_name_plural = 'Запрещенные слова'
        ordering = ('word',)

    def __str__(self) -> str:
        """Display Profanity word in admin panel."""
        return self.word[:CHARS_LIMIT]
