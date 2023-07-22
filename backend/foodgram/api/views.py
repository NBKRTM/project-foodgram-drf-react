from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import permissions, filters, viewsets, status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Favorite)
from users.models import User, Follow
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeReadSerializer,
                          RecipePostUpdateSerializer,
                          ShortRecipeSerializer,
                          UserGetSerializer,
                          UserPostSerializer)
from .permissions import IsAuthorOrAdminOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserGetSerializer
        else:
            return UserPostSerializer

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated, ])
    def subscriptions(self):
        pass

    @action(detail=False, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated, ])
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk)

        if request.method == 'POST':
            if not request.user.is_authenticated:
                return Response({"detail": 'Авторизуйтесь для подписки'},
                                status=status.HTTP_401_UNAUTHORIZED)

            if request.user == author:
                return Response({"detail": 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)

            follow, created = Follow.objects.get_or_create(
                user=request.user, author=author)

            if not created and request.method == 'POST':
                return Response(
                    {"detail": 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": 'Подписка успешно создана'},
                            status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not request.user.is_authenticated:
                return Response({"detail": 'Авторизуйтесь для отписки'},
                                status=status.HTTP_401_UNAUTHORIZED)

            try:
                follow = Follow.objects.get(user=request.user,
                                            author=author)
                follow.delete()
                return Response(
                    {"detail": 'Вы отписались от данного пользователя'},
                    status=status.HTTP_204_NO_CONTENT)

            except Follow.DoesNotExist:
                return Response(
                    {"detail": 'Вы не были подписаны на данного пользователя'},
                    status=status.HTTP_404_NOT_FOUND)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()


# recipes app
class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['author']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        else:
            return RecipePostUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_recipe_object(self, pk):
        return get_object_or_404(Recipe, pk=pk)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk):
        recipe = self.get_recipe_object(pk)

        if request.method == 'POST':
            if not request.user.is_authenticated:
                return Response(
                    {"detail": 'Авторизуйтесь для добавления в избранное'},
                    status=status.HTTP_401_UNAUTHORIZED)

            if Favorite.objects.filter(
                    user=request.user, recipe=recipe).exists():
                return Response({"errors": 'Рецепт уже добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)

            Favorite.objects.create(user=request.user, recipe=recipe)

            serializer = ShortRecipeSerializer(recipe, data=request.data,
                                               context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not request.user.is_authenticated:
                return Response(
                    {"detail": 'Авторизуйтесь для удаления из избранного'},
                    status=status.HTTP_401_UNAUTHORIZED)

            try:
                favorite = get_object_or_404(Favorite, user=request.user,
                                             recipe=recipe)
                favorite.delete()
                return Response({"detail": 'Рецепт успешно удален'},
                                status=status.HTTP_204_NO_CONTENT)

            except Favorite.DoesNotExist:
                return Response({"errors": 'Данного рецепта нет в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk):
        recipe = self.get_recipe_object(pk)

        if request.method == 'POST':
            if not request.user.is_authenticated:
                return Response(
                    {"detail": 'Авторизуйтесь для добавления в корзину'},
                    status=status.HTTP_401_UNAUTHORIZED)

            if ShoppingCart.objects.filter(
                    user=request.user, recipe=recipe).exists():
                return Response({"errors": 'Рецепт уже добавлен в корзину'},
                                status=status.HTTP_400_BAD_REQUEST)

            ShoppingCart.objects.create(user=request.user, recipe=recipe)

            serializer = ShortRecipeSerializer(recipe, data=request.data,
                                               context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not request.user.is_authenticated:
                return Response(
                    {"detail": 'Авторизуйтесь для удаления из корзины'},
                    status=status.HTTP_401_UNAUTHORIZED)

            try:
                shopping_cart = get_object_or_404(ShoppingCart,
                                                  user=request.user,
                                                  recipe=recipe)
                shopping_cart.delete()
                return Response({"detail": 'Рецепт успешно удален из корзины'},
                                status=status.HTTP_204_NO_CONTENT)

            except ShoppingCart.DoesNotExist:
                return Response({"errors": 'Данного рецепта нет в корзине'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, pk):

        if not request.user.is_authenticated:
            return Response(
                {"detail": 'Авторизуйтесь для скачивания списка покупок'}
            )

        shopping_cart_recipes = ShoppingCart.objects.filter(user=request.user)
        ingredient_quantities = {}

        for cart_recipe in shopping_cart_recipes:
            recipe_ingredients = RecipeIngredient.objects.filter(
                recipe=cart_recipe.recipe)
            for recipe_ingredient in recipe_ingredients:
                ingredient_name = recipe_ingredient.ingredient.name
                ingredient_unit = recipe_ingredient.ingredient.measurement_unit
                ingredient_amount = recipe_ingredient.amount

                ingredient_key = f"{ingredient_name} ({ingredient_unit})"
                if ingredient_key in ingredient_quantities:
                    ingredient_quantities[ingredient_key] += ingredient_amount
                else:
                    ingredient_quantities[ingredient_key] = ingredient_amount

        file_content = "\n".join([f"{key} — {value}" for key, value
                                 in ingredient_quantities.items()])

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=shop_cart.txt'
        response.write(file_content)

        return response
