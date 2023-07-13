from django.db import models
from django.core.validators import MinValueValidator
from foodgram.settings import RECIPES_MAX_LENGTH
from .validators import create_hex_validator, create_slug_validator
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=RECIPES_MAX_LENGTH,
        unique=True,
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7,
        unique=True,
        validators=[create_hex_validator()]
    )
    slug = models.CharField(
        'Уникальный slug',
        max_length=RECIPES_MAX_LENGTH,
        unique=True,
        validators=[create_slug_validator()]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=RECIPES_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=RECIPES_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название',
        max_length=RECIPES_MAX_LENGTH,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
    )
    text = models.TextField(
        'Текстовое описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Список ингредиентов',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredient_recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Состав рецепта'
        verbose_name_plural = 'Состав рецепта'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients'
            )
        ]


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart'
            )
        ]


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorited'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite'
    )

    class Meta:
        verbose_name = 'Рецепт в Избранном'
        verbose_name_plural = 'Рецепты в Избранном'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite'
            )
        ]
