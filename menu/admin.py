from django.contrib import admin

from menu.models import Category, FoodItem


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name", "parent", "slug", "vendor", "created_at")


class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("food_title", "vendor", "category")


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
