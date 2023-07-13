from django.contrib import admin
from .models import (Tag, Ingredient,
                     Recipe, RecipeIngredient, ShoppingCart, Favorite)


class IngredientAdmin(admin.TabularInline):
    model = RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        IngredientAdmin,
    ]
    filter_horizontal = ('ingredients',)


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
