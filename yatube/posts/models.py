from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор', )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Пост'

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=False,
        null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=False,
        null=True)
    text = models.TextField('Текст комментария')

    class Meta(CreatedModel.Meta):
        verbose_name = 'Комментарий'


class Follow(CreatedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        blank=False,
        null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        blank=False)
