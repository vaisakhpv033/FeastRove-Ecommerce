from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserProfile


class CustomUserAdmin(UserAdmin):
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    list_display = ("email", "first_name", "last_name", "role", "is_active")
    ordering = ("-date_joined",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
