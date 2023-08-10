from django.db.models import F

from users.models import Follow
from recipes.models import RecipeIngredient, Ingredient


def get_subscribed(obj, request):
    # request = self.context.get('request').user.id
    if request is None or request.user.is_anonymous:
        return False
    return Follow.objects.filter(user=request.user, author=obj).exists()


def create_recipe_ingredient(recipe, ingredients_data):
    ingredients = []
    for ingredient_data in ingredients_data:
        ingredient_id = ingredient_data['ingredient']['id']
        amount = ingredient_data['amount']
        ingredient = Ingredient.objects.get(id=ingredient_id)
        existing_recipe_ingredient = RecipeIngredient.objects.filter(
            recipe=recipe,
            ingredient=ingredient_id)
        if existing_recipe_ingredient.exists():
            existing_recipe_ingredient.update(amount=F('amount') + amount)
        else:
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
            ingredients.append(recipe_ingredient)
    RecipeIngredient.objects.bulk_create(ingredients)
