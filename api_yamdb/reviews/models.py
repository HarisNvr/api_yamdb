import string
import random

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache


class CustomUser(AbstractUser):
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
