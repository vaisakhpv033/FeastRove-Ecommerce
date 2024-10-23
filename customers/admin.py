from django.contrib import admin
from .models import State, Address, Favourites

# Register your models here.
admin.site.register(State)
admin.site.register(Address)
admin.site.register(Favourites)