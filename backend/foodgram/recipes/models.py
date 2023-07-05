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
        blank=False
    )
    color = models.CharField(
        'Цветовой HEX-код',
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
        'Название ингредиента',
        max_length=RECIPES_MAX_LENGTH,
        blank=False
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=RECIPES_MAX_LENGTH,
        blank=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
        blank=False
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=False
    )
    text = models.TextField(
        'Текстовое описание',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов',
        blank=False
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(1)],
        blank=False
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
    )


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_shopping_cart'
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
