from datetime import datetime as dt

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator, \
    MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

MX_CHARS = 256


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField('Права доступа',
                            max_length=20,
                            choices=(('user', 'User'),
                                     ('moderator', 'Moderator'),
                                     ('admin', 'Admin')),
                            default='user')
    bio = models.TextField('Биография', blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    name = models.CharField(
        max_length=MX_CHARS,
        verbose_name='Название',
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=False,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы '
                  'латиницы, цифры, дефис и подчёркивание.',
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Идентификатор страницы должен содержать только '
                        'латинские символы, цифры, дефис и подчёркивание.',
                code='invalid_slug'
            )
        ]
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=MX_CHARS,
        verbose_name='Название',
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=False,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы '
                  'латиницы, цифры, дефис и подчёркивание.',
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Идентификатор страницы должен содержать только '
                        'латинские символы, цифры, дефис и подчёркивание.',
                code='invalid_slug'
            )
        ]
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=MX_CHARS,
        verbose_name='Название',
        blank=False
    )
    year = models.IntegerField(
        verbose_name='Год выхода',
        blank=False
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        blank=False,
        verbose_name='Жанр',
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        blank=False,
        verbose_name='Категория',
        related_name='titles'
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def calculate_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total_score = sum(review.score for review in reviews)
            num_reviews = reviews.count()
            return total_score / num_reviews
        else:
            return None

    def clean(self):
        super().clean()
        if self.year < 0:
            raise ValidationError(
                {'year': 'Год создания не может быть отрицательным числом!'}
            )
        elif self.year > dt.now().year:
            raise ValidationError(
                {'year': 'Год создания не может быть больше текущего!'}
            )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.achievement} {self.cat}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='ID_Произведения'
    )
    text = models.TextField(
        verbose_name='Текст обзора',
        blank=False
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='reviews'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1, message='Оценка не может быть ниже 1'),
            MaxValueValidator(10, message='Оценка не может быть больше 10')
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан'
    )

    class Meta:
        verbose_name = 'обзор'
        verbose_name_plural = 'Обзоры'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='commentaries',
        verbose_name='ID_Обзора'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Создан')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='commentaries')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class ActivationeCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=6)

    class Meta:
        verbose_name = 'Код активации'
        verbose_name_plural = 'Коды активации'
