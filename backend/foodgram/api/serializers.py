from rest_framework import serializers

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Favorite)

from users.models import User, Follow
from .validators import validate_username
# users app


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed']

    def validate_username(self, username):
        return validate_username(username)

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=user).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    def validate_username(self, username):
        return validate_username(username)


class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ['current_password', 'new_password']
# recipes app


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'recipe', 'ingredient', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredient', many=True)
    tags = TagSerializer(many=True)
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and Favorite.objects.filter(
            recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and ShoppingCart.objects.filter(
            recipe=obj, user=request.user).exists()
