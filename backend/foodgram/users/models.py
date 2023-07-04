from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.settings import USERS_MAX_LENGHT
from .validators import create_username_validator


class User(AbstractUser):
    email = models.EmailField(
        max_length=254
    )
    username = models.CharField(
        max_length=USERS_MAX_LENGHT,
        unique=True,
        validators=[create_username_validator()]
    )
    first_name = models.CharField(
        max_length=USERS_MAX_LENGHT
    )
    last_name = models.CharField(
        max_length=USERS_MAX_LENGHT
    )
    password = models.CharField(
        max_length=USERS_MAX_LENGHT
    )
