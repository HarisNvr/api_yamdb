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


class ActivationeCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=6)

    class Meta:
        verbose_name = 'Код активации'
        verbose_name_plural = 'Коды активации'
