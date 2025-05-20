from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from .constants import COMMENT_TEXT_SNIPPET_LENGTH


User = get_user_model()


class PublishedCreatedModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Category(PublishedCreatedModel):
    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedCreatedModel):
    name = models.CharField(
        'Название места',
        max_length=256
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedCreatedModel):
    title = models.CharField(
        'Публикация',
        max_length=256
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        default=timezone.now,
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text='Загрузите изображение для публикации',
    )
    # is_published = models.BooleanField(
    #     'Опубликовано',
    #     default=True,
    #     help_text='Снимите галочку, чтобы скрыть пост'
    # )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )
    text = models.TextField('Текст комментария')
    created_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        ordering = ['created_date']
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        text_snippet = self.text[:COMMENT_TEXT_SNIPPET_LENGTH]
        return (
            f'Комментарий от {self.author.username} '
            f'к посту "{self.post}" '
            f'от {self.created_date.strftime("%Y-%m-%d %H:%M")} '
            f'Текст: "{text_snippet}..."'
        )
