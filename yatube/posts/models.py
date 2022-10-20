from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
LIMIT_POST: int = 15


class Group(models.Model):
    title = models.CharField(
        verbose_name='Заголовок группы',
        max_length=200,
        help_text='Придумайте название группы')
    slug = models.SlugField(
        verbose_name='Адрес для страницы группы',
        max_length=100,
        unique=True)
    description = models.TextField(
        verbose_name='Описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Расскажите о чём-то интересном')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста')
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        related_name='posts',
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Выберите группу')
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Размер картинки 960 на 339, картинки обрезаются',
        upload_to='posts/',
        blank=True)

    def __str__(self):
        return self.text[: LIMIT_POST]

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments')

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                                    fields=['author', 'user'], 
                                    name='unique subs')
        ]
