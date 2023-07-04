from django.db import models
from django.core.validators import MinValueValidator
from foodgram.settings import RECIPES_MAX_LENGHT
from .validators import create_hex_validator, create_slug_validator


class Tag(models.Model):
    name = models.CharField(
        max_length=RECIPES_MAX_LENGHT,
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
        max_length=200,
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
        max_length=RECIPES_MAX_LENGHT,
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=RECIPES_MAX_LENGHT,
        blank=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey()
    name = models.CharField(
        max_length=RECIPES_MAX_LENGHT,
        blank=False
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False
    )
    text = models.TextField(
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
        validators=[MinValueValidator(1)],
        blank=False
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    pass


class Favorite(models.Model):
    pass
