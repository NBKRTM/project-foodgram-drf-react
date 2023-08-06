from users.models import Follow
from recipes.models import RecipeIngredient


def get_subscribed(obj, request):
    # request = self.context.get('request').user.id
    if request is None or request.user.is_anonymous:
        return False
    return Follow.objects.filter(user=request.user, author=obj).exists()


def create_recipe_ingredient(recipe, ingredients_data):
    recipe_ingredients = [
        RecipeIngredient(
            recipe=recipe,
            ingredient_id=ingredient_data['pk'],
            amount=ingredient_data['amount']
        )
        for ingredient_data in ingredients_data
    ]
    RecipeIngredient.objects.bulk_create(recipe_ingredients)
