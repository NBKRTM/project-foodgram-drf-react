from rest_framework import serializers

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Favorite)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredient(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cocking_time',
                  'is_favorited', 'is_in_shopping_cart']
