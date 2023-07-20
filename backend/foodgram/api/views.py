from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import permissions, filters, viewsets, status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
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
                          UserSerializer)
from .permissions import IsAuthorOrAdminOrReadOnly


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
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['author']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        else:
            return RecipePostUpdateSerializer

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            if Favorite.objects.filter(
                    user=request.user, recipe=recipe).exists():
                return Response({"errors": 'Рецепт уже добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=request.user, recipe=recipe)

            serializer = ShortRecipeSerializer(recipe, data=request.data,
                                               context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not request.user.is_authenticated:
                return Response(
                    {"errors": 'Вы должны быть авторизованы для удаления'},
                    status=status.HTTP_401_UNAUTHORIZED)

            try:
                favorite = get_object_or_404(Favorite, user=request.user,
                                             recipe=recipe)
                favorite.delete()
                return Response({"errors": 'Рецепт успешно удален'},
                                status=status.HTTP_204_NO_CONTENT)

            except Favorite.DoesNotExist:
                return Response({"errors": 'Данного рецепта нет в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
