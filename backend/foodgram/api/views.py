from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from foodgram.settings import FILENAME
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.models import Follow, User
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipePostUpdateSerializer, RecipeReadSerializer,
                          ShortRecipeSerializer, TagSerializer,
                          UserGetSerializer, UserPostSerializer,
                          ChangePasswordSerializer,
                          FavoriteSerializer, ShoppingCartSerializer)
from .filters import IngredientFilter, RecipeFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny, )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserGetSerializer
        elif self.action == 'favorite':
            return FavoriteSerializer
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
        else:
            return UserPostSerializer

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = ChangePasswordSerializer(
            request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated, ])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page, many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated, ])
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = FollowSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            if request.user == author:
                return Response({"detail": 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)

            _, created = Follow.objects.get_or_create(
                user=request.user, author=author)

            if not created:
                return Response(
                    {"detail": 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": 'Подписка успешно создана'},
                            status=status.HTTP_201_CREATED)

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


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        elif self.action == 'favorite':
            return FavoriteSerializer
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return RecipePostUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def shortrecipe_get_serializer(self, recipe, request):
        serializer = ShortRecipeSerializer(recipe, data=request.data,
                                           context={"request": request})
        serializer.is_valid(raise_exception=True)
        return serializer

    def recipe_get(self, recipe, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        return recipe

    def create_or_delete_object(self, request, recipe, model_class):
        serializer = self.shortrecipe_get_serializer(recipe, request)

        if not model_class.objects.filter(user=request.user,
                                          recipe=recipe).exists():
            model_class.objects.create(user=request.user, recipe=recipe)
            serializer.save(user=request.user, recipe=recipe)
            status_code = status.HTTP_201_CREATED
            success_response = {"detail": "Рецепт успешно добавлен."}
        else:
            object_to_delete = get_object_or_404(
                model_class, user=request.user, recipe=recipe)
            object_to_delete.delete()
            status_code = status.HTTP_204_NO_CONTENT
            success_response = {"detail": "Рецепт успешно удален."}

        return Response(success_response, status=status_code)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, **kwargs):
        recipe = self.recipe_get(Recipe, **kwargs)
        return self.create_or_delete_object(request, recipe, Favorite)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, **kwargs):
        recipe = self.recipe_get(Recipe, **kwargs)
        return self.create_or_delete_object(request, recipe, ShoppingCart)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        shopping_cart_recipes = ShoppingCart.objects.filter(user=request.user)
        recipe_ids = shopping_cart_recipes.values_list('recipe_id', flat=True)

        ingredient_quantities = RecipeIngredient.objects.filter(
            recipe__id__in=recipe_ids
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount')
        )

        file_content = "\n".join(
            [f"{item['ingredient__name']} "
             f"({item['ingredient__measurement_unit']}) "
             f"— {item['total_amount']}" for item in ingredient_quantities]
        )

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={FILENAME}'
        response.write(file_content)

        return response
