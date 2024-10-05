from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import cache_control
from .forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.utils import check_role_vendor
from accounts.models import UserProfile
from .models import Vendor
from django.contrib import messages
from menu.models import Category, FoodItem
from menu.forms import CategoryForm
from django.db.models import Q

# Create your views here.
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance = profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Profile Updated successfully')
            return redirect('vendorProfile')
    else:   
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/vendorProfile.html', context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_menu_builder(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = Category.objects.filter(fooditem__vendor=vendor).distinct()
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/vendorMenuBuilder.html', context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_fooditems_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    vendor = Vendor.objects.get(user=request.user)
    food_items = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'food_items': food_items,
        'category': category
    }
    return render(request, 'vendor/foodItemsCategory.html', context)



@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully")
            return redirect("vendorAddCategory")

    context = {
        'form': form,
    }
    return render(request, 'vendor/categoryAdd.html', context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_edit_category(request, slug):
    category = get_object_or_404(Category, Q(slug=slug) & Q(parent__isnull=False))
    form = CategoryForm(instance=category)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully")
            return redirect("vendorMenuBuilder")

    context = {
        'form': form,
        'category': category,
    }
    return render(request, "vendor/editCategory.html", context)


