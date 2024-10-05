from django.contrib import admin

from menu.models import Category, FoodItem


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
        list_display = ('category_name', 'parent', 'slug', 'created_at')
        #list_display_links = ('user', 'vendor_name')


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem)