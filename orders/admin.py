from django.contrib import admin
from .models import Order, OrderedFood, Payment
# Register your models here.

# class OrderedFoodOnline(admin.TabularInline):
#     model = OrderedFood
#     readonly_fields = ('order', 'payment', 'user', 'Fooditem', 'quantity', 'price')
#     extra = 0

# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['order_number', 'name', 'phone', 'email', 'total', 'payment_method', 'status', 'is_ordered']
#     inlines = [OrderedFoodOnline]

admin.site.register(Order)
admin.site.register(OrderedFood)
admin.site.register(Payment)