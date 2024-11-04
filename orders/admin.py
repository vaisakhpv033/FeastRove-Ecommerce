from django.contrib import admin
from .models import Order, OrderedFood, Payment
# Register your models here.

class OrderedFoodOnline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('order', 'payment', 'user', 'fooditem', 'quantity', 'price')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone_number', 'email', 'total', 'payment_method', 'status', 'is_ordered']
    inlines = [OrderedFoodOnline]

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'payment_method', 'status', 'amount', 'user']


class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment', 'user', 'fooditem', 'quantity', 'price']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood, OrderedFoodAdmin)
admin.site.register(Payment, PaymentAdmin)