from django.contrib import admin
from .models import Tag, Ingredient, Recipe, ShoppingCart, Favorite

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
