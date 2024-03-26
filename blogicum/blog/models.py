from django.db import models
from django.contrib.auth import get_user_model

from core.models import PublishedModel

CHARS_LIMIT: int = 30

User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(
        'Заголовок',
        max_length=256
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
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:CHARS_LIMIT]


class Location(PublishedModel):
    name = models.CharField(
        verbose_name='Название места',
        max_length=256
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:CHARS_LIMIT]


class Post(PublishedModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=256
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
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
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.title[:CHARS_LIMIT]


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
