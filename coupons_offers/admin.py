from django.contrib import admin
from .models import Coupons
# Register your models here.

class CouponsAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_amount', 'min_order_value', 'max_discount', 'is_active', 'usage_limit', 'user_limit']

admin.site.register(Coupons, CouponsAdmin)