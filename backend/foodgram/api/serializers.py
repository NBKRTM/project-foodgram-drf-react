from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer

from api.utils import get_subscribed, create_recipe_ingredient
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.models import User
from .validators import validate_new_username


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return get_subscribed(obj, request)


class UserPostSerializer(UserCreateSerializer):
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

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

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
        model = Ingredient()
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

    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError(
                'Количество ингредиента должно быть больше 0'
            )
        return value


class RecipeReadSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        source='ingredient_recipe',
        many=True,
        read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=True)

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
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = request.GET.get('recipe')
        ingredient_id = data['ingredient']['id']
        existing_ingredients = RecipeIngredient.objects.filter(
            recipe_id=recipe_id,
            ingredient_id=ingredient_id
        )
        if existing_ingredients.exists():
            raise ValidationError('Ингредиент уже добавлен в рецепт')
        return data


class RecipePostUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    author = UserGetSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = ['id', 'ingredients', 'tags', 'author',
                  'name', 'image', 'text', 'cooking_time']

    def validate(self, data):
        ingredients_list = []
        ingredients_data = data.get('ingredients')
        cooking_time = data.get('cooking_time')
        tags = data.get('tags')
        for ingredient in data.get('ingredients'):
            if ingredient.get('amount') <= 0:
                raise ValidationError(
                    'Количество ингредиента не может быть меньше 1'
                )
            ingredients_list.append(ingredient.get('ingredient')['id'])
        if len(set(ingredients_list)) != len(ingredients_list):
            raise ValidationError(
                'В рецепт нельзя добавить одинаковые ингредиенты!'
                'Следует увеличить количество текущего ингредиента!'
            )
        if not ingredients_data or len(ingredients_data) < 1:
            raise ValidationError(
                "Рецепт должен содержать хотя бы один ингредиент.")
        if cooking_time <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 0.')
        if not tags:
            raise ValidationError('Необходимо указать теги.')
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        create_recipe_ingredient(recipe, ingredients_data)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipe=instance).delete
        create_recipe_ingredient(instance, ingredients_data)
        instance.tags.set(tags_data)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance,
                                    context=self.context).data


class FavoriteSerializer(serializers.Serializer):
    def validate(self, data):
        recipe_id = self.context['recipe_id']
        user = self.context['request'].user
        if Favorite.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists():
            raise ValidationError(
                'Этот рецепт уже есть в избранном.'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, id=validated_data['id'])
        user = self.context['request'].user
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return serializer.data


class ShoppingCartSerializer(serializers.Serializer):
    def validate(self, data):
        recipe_id = self.context['recipe_id']
        user = self.context['request'].user
        if ShoppingCart.objects.filter(
            user=user, recipe_id=recipe_id
        ).exists():
            raise ValidationError(
                'Этот рецепт уже есть в списке покупок.'
            )
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['id'])
        ShoppingCart.objects.create(
            user=self.context['request'].user,
            recipe=recipe
        )
        serializer = ShortRecipeSerializer(recipe)
        return serializer.data
