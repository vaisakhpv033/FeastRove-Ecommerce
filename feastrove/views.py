from django.shortcuts import render
from django.views.decorators.cache import cache_control
from vendor.models import Vendor
from menu.models import FoodItem

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:4]
    food_items = FoodItem.objects.filter(is_available=True)
    context = {
        'restaurants': vendors,
        'food_items': food_items,
    }
    return render(request, 'base_layouts/home.html', context)