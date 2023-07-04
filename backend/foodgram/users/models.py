from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.settings import USERS_MAX_LENGTH
from .validators import create_username_validator


class User(AbstractUser):
    email = models.EmailField(
        max_length=254
    )
    username = models.CharField(
        max_length=USERS_MAX_LENGTH,
        unique=True,
        validators=[create_username_validator()]
    )
    first_name = models.CharField(
        max_length=USERS_MAX_LENGTH
    )
    last_name = models.CharField(
        max_length=USERS_MAX_LENGTH
    )
    password = models.CharField(
        max_length=USERS_MAX_LENGTH
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follower'
            )
        ]

    def __str__(self):
        return (
            f'Юзер {self.user.username}'
            f'Подписан на {self.following.get_username}'
        )
