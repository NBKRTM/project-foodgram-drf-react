from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.utils import get_subscribed, create_recipe_ingredient
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.models import User
from .validators import validate_new_username


class UserGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return get_subscribed(obj, request)


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'password']

    def validate_username(self, username):
        return validate_new_username(username)

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ['current_password', 'new_password']


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return get_subscribed(obj, request)

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeReadSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredient',
        many=True)
    tags = TagSerializer(many=True)
    author = UserGetSerializer()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and Favorite.objects.filter(
            recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and ShoppingCart.objects.filter(
            recipe=obj, user=request.user).exists()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipePostUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    author = UserGetSerializer()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'ingredients', 'tags', 'author',
                  'name', 'image', 'text', 'cooking_time']

    def validate_ingredients(self, value):
        ingredient_names = [item['name'] for item in value]
        if len(ingredient_names) != len(set(ingredient_names)):
            raise serializers.ValidationError('Дублирование ингредиентов!')
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        create_recipe_ingredient(recipe, ingredients_data)

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        instance = super().update(instance, validated_data)

        instance.recipe_ingredient.all().delete()

        create_recipe_ingredient(instance, ingredients_data)

        instance.tags.set(tags_data)

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']
