from django.db import models
from .validators import create_hex_validator, create_slug_validator


class Tag(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        blank=False
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        blank=False,
        validators=[create_hex_validator()]
    )
    slug = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        validators=[create_slug_validator()]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=150,
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=150,
        blank=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=150,
        blank=False
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False
    )
    text = models.TextField(
        max_length=150,
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False
    )
    cooking_time = models.PositiveIntegerField(
        max_length=150,
        blank=False)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
