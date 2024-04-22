from datetime import datetime as dt

from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import (
    MX_CHARS,
    MX_CHARS_BIG,
    MX_CHARS_STR,
    MIN_REVIEW_SCORE,
    MAX_REVIEW_SCORE
)


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField('Права доступа',
                            max_length=20,
                            choices=(('user', 'User'),
                                     ('moderator', 'Moderator'),
                                     ('admin', 'Admin')),
                            default='user')
    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.CharField(max_length=6)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class CategoryGenre(models.Model):
    name = models.CharField(
        max_length=MX_CHARS_BIG,
        verbose_name='Название',
        unique=True,
    )
    slug = models.SlugField(
        max_length=MX_CHARS,
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы '
                  'латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:MX_CHARS_STR] + "..." if (
                len(self.name) > MX_CHARS_STR
        ) else self.name


class Category(CategoryGenre):
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenre):
    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=MX_CHARS_BIG,
        verbose_name='Название'
    )
    year = models.SmallIntegerField(
        verbose_name='Год выхода',
        validators=[
            MaxValueValidator(
                dt.now().year,
                message='Год не может быть больше текущего.'
            )
        ]
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанр',
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        verbose_name='Категория',
        related_name='titles'
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MX_CHARS_STR] + "..." if (
                len(self.name) > MX_CHARS_STR
        ) else self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'жанр произведения'
        verbose_name_plural = 'Жанры произведений'


class ReviewComment(models.Model):
    text = models.TextField(verbose_name='Содержание')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:MX_CHARS_STR] + "..." if (
                len(self.text) > MX_CHARS_STR
        ) else self.text


class Review(ReviewComment):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.SmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(
                MIN_REVIEW_SCORE,
                message=f'Оценка не может быть ниже {MIN_REVIEW_SCORE}'
            ),
            MaxValueValidator(
                MAX_REVIEW_SCORE,
                message=f'Оценка не может быть больше {MAX_REVIEW_SCORE}'
            )
        ]
    )

    class Meta:
        verbose_name = 'обзор'
        verbose_name_plural = 'Обзоры'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_title_author'
            )
        ]
        ordering = ('-pub_date',)


class Comment(ReviewComment):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='commentaries',
        verbose_name='Обзор'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
