from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_control

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.utils import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem

from .forms import VendorForm
from .models import Vendor


# Create your views here.
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Profile Updated successfully")
            return redirect("vendorProfile")
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        "profile_form": profile_form,
        "vendor_form": vendor_form,
        "profile": profile,
        "vendor": vendor,
    }
    return render(request, "vendor/vendorProfile.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_menu_builder(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = Category.objects.filter(fooditem__vendor=vendor).distinct()
    context = {
        "categories": categories,
    }
    return render(request, "vendor/vendorMenuBuilder.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_fooditems_category(request, slug):
    vendor = Vendor.objects.get(user=request.user)
    category = get_object_or_404(Category, slug=slug, vendor=vendor)
    food_items = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {"food_items": food_items, "category": category}
    return render(request, "vendor/foodItemsCategory.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_add_category(request):
    vendor = Vendor.objects.get(user=request.user)
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.vendor = vendor
            category.save()
            messages.success(request, "Category added successfully")
            return redirect("vendorAddCategory")

    context = {
        "form": form,
    }
    return render(request, "vendor/categoryAdd.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_edit_category(request, slug):
    vendor = Vendor.objects.get(user=request.user)
    category = get_object_or_404(
        Category, Q(slug=slug) & Q(parent__isnull=False) & Q(vendor=vendor)
    )
    form = CategoryForm(instance=category)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully")
            return redirect("vendorMenuBuilder")

    context = {
        "form": form,
        "category": category,
    }
    return render(request, "vendor/editCategory.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_add_food(request):
    vendor = Vendor.objects.get(user=request.user)
    form = FoodItemForm(vendor=vendor)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, vendor=vendor)
        if form.is_valid():
            form = form.save(commit=False)
            form.vendor = vendor
            form.save()
            messages.success(request, "Food Item added Successfully")
            return redirect("vendorFoodItemsCategory", form.category.slug)
        else:
            print(form.errors)

    context = {
        "form": form,
    }
    return render(request, "vendor/addFood.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_edit_food(request, slug):
    vendor = Vendor.objects.get(user=request.user)
    food = get_object_or_404(FoodItem, slug=slug, vendor=vendor)
    form = FoodItemForm(instance=food, vendor=vendor)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food, vendor=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, "FoodItem updated successfully")
            return redirect("vendorFoodItemsCategory", food.category.slug)

    context = {
        "form": form,
        "slug": slug,
    }

    return render(request, "vendor/editFood.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_food_details(request, slug):
    vendor = Vendor.objects.get(user=request.user)
    food = get_object_or_404(FoodItem, slug=slug, vendor=vendor)
    if request.method == "POST":
        food.is_available = not food.is_available
        food.save()
        return redirect("vendorFoodDetails", slug)

    context = {
        "food_item": food,
    }
    return render(request, "vendor/foodDetails.html", context)
