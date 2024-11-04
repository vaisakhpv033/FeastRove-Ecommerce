from django.contrib import admin

from .models import VendorReview


class VendorReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'order', 'created_at']
# Register your models here.
admin.site.register(VendorReview, VendorReviewAdmin)
