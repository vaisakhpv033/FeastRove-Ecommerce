from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_POST

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.utils import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from orders.models import Order, OrderedFood
from reviews.models import VendorReview

from .forms import VendorForm
from .models import Vendor

VALID_STATUS_TRANSITIONS = {
    "New": ["Accepted", "Cancelled"],
    "Accepted": ["Completed", "Cancelled"],
    "Completed": [],
    "Cancelled": [],
}


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_dashboard(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    orders = Order.objects.filter(vendor=vendor, is_ordered=True).order_by('-created_at')

    order_summary = orders.aggregate(
        total_order_count = Count('id'),
        completed_count = Count('id', filter=Q(status='Completed')),
        cancelled_count = Count('id', filter=Q(status='Cancelled'))
    )

    total_revenue = orders.aggregate(
        total_sum = Sum('total', filter=Q(status='Completed')),
        total_tax = Sum('total_tax', filter=Q(status='Completed')),
        total_cancelled = Sum('total', filter=Q(status='Cancelled'))
        )
    rated_orders = VendorReview.objects.filter(order__vendor=vendor, rating__isnull=False)

    average_rating = rated_orders.aggregate(
        avg_rating = Avg('rating'),
        rating_count = Count('rating'),
        one_rating = Count('rating', filter=Q(rating=1)),
        two_rating = Count('rating', filter=Q(rating=2)),
        three_rating = Count('rating', filter=Q(rating=3)),
        four_rating = Count('rating', filter=Q(rating=4)),
        five_rating = Count('rating', filter=Q(rating=5))
    )

    context = {
        'order': orders,
        'order_summary': order_summary,
        'total_revenue': total_revenue,
        'average_rating': average_rating,
    }
    return render(request, "accounts/vendorDashboard.html", context)


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


# Vendor orders


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_orders_all(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    orders = Order.objects.filter(vendor=vendor, is_ordered=True).order_by("-created_at")
    context = {
        "orders": orders,
        "VALID_STATUS_TRANSITIONS": VALID_STATUS_TRANSITIONS,
    }
    return render(request, "vendor/OrdersAll.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@require_POST
def vendor_update_order_status(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        new_status = request.POST.get("status")
        order_number = request.POST.get("order_number")
        vendor = get_object_or_404(Vendor, user=request.user)
        order = get_object_or_404(Order, order_number=order_number, vendor=vendor)

        if new_status in VALID_STATUS_TRANSITIONS[order.status]:
            order.status = new_status
            order.save()
            print(new_status, order_number)
            return JsonResponse(
                {
                    "status": "Success",
                    "message": "Updated the status successfully",
                    "order_status": order.status,
                }
            )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid status"})




@login_required(login_url="login")
@user_passes_test(check_role_vendor)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def vendor_my_order_details(request, order_number):
    vendor = get_object_or_404(Vendor, user=request.user)
    order = get_object_or_404(
        Order, order_number=order_number, vendor=vendor, is_ordered=True
    )
    order_items = OrderedFood.objects.filter(order=order)

    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request, "vendor/vendorMyOrderDetails.html", context)