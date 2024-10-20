from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control

from menu.models import Category, FoodItem
from vendor.models import Vendor
from customers.models import Address
from .context_processors import get_cart_count, get_cart_total
from .models import Cart

# Create your views here.


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    print(vendors)
    for i in vendors:
        print(i.vendor_slug)
    context = {
        "restaurants": vendors,
    }
    return render(request, "marketplace/restaurantListing.html", context)


def restaurant_details(request, vendor_slug, category_slug=None):
    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor)
    if category_slug:
        category = Category.objects.get(slug=category_slug)
        fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    else:
        fooditems = FoodItem.objects.filter(vendor=vendor)
    context = {
        "vendor": vendor,
        "categories": categories,
        "fooditems": fooditems,
    }
    return render(request, "marketplace/restaurantAllDetails.html", context)


def restaurant_category_details(request, vendor_slug, category_slug):
    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor)
    category = Category.objects.get(slug=category_slug)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        "vendor": vendor,
        "category": categories,
        "fooditems": fooditems,
    }
    return render(request, "marketplace/restaurantCategoryDetails.html", context)


def food_item_details(request, slug):
    food_item = FoodItem.objects.get(slug=slug)
    context = {
        "food_item": food_item,
    }
    return render(request, "marketplace/fooditemDetails.html", context)


@login_required(login_url="login")
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("-created_at")
    context = {
        "cart_items": cart_items,
    }
    return render(request, "marketplace/cart.html", context)


def add_to_cart(request, slug):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # Check if the fooditem exists
            try:
                fooditem = FoodItem.objects.get(slug=slug)

                # Try to get the cart item or create it if it doesn't exist
                cart_item, created = Cart.objects.get_or_create(
                    user=request.user, fooditem=fooditem, defaults={"quantity": 1}
                )

                if not created:
                    # increment the quantity if quantity less than 5
                    if cart_item.quantity >= 5:
                        return JsonResponse(
                            {
                                "status": "Failed",
                                "message": "Maximum allowed quantity is 5",
                            }
                        )

                    cart_item.quantity = F("quantity") + 1
                    cart_item.save()
                    cart_item.refresh_from_db()  # refresh the object to get the updated quantity
                return JsonResponse(
                    {
                        "status": "Success",
                        "message": "Successfully added to the cart"
                        if created
                        else "Increased the cart quantity",
                        "cart_counter": get_cart_count(request),
                        "item_qty": cart_item.quantity,
                        "cart_amounts": get_cart_total(request),
                        "total_price": cart_item.total_price,
                    }
                )

            except FoodItem.DoesNotExist:
                return JsonResponse(
                    {"status": "Failed", "message": "This food doesn't exist"}
                )

            except Exception as e:
                print(e)
                return JsonResponse({"status": "Failed", "message": "An error Occured"})

        else:
            return JsonResponse({"status": "Failed", "message": "Invalid request"})
    else:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )


def decrease_from_cart(request, slug):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # Check if the fooditem exists
            try:
                food_item = FoodItem.objects.get(slug=slug)
                cart_item = Cart.objects.get(user=request.user, fooditem=food_item)
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                    item_qty = cart_item.quantity
                    total_price = cart_item.total_price
                else:
                    cart_item.delete()
                    item_qty = 0
                    total_price = 0

                return JsonResponse(
                    {
                        "status": "Success",
                        "message": "Decreased the cart quantity",
                        "cart_counter": get_cart_count(request),
                        "item_qty": item_qty,
                        "cart_amounts": get_cart_total(request),
                        "total_price": total_price,
                    }
                )
            except (FoodItem.DoesNotExist, Cart.DoesNotExist):
                return JsonResponse(
                    {
                        "status": "Failed",
                        "message": "Item doesn't exist in the cart",
                        "cart_counter": get_cart_count(request),
                    }
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid request"})
    else:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )


def remove_cart_item(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                cart_item.delete()
                return JsonResponse(
                    {
                        "status": "Success",
                        "message": "Cart Item has been deleted",
                        "cart_counter": get_cart_count(request),
                        "cart_amounts": get_cart_total(request),
                    }
                )
            except Cart.DoesNotExist:
                return JsonResponse(
                    {"status": "Failed", "message": "Item doesn't exist"}
                )
            except Exception as e:
                print(e)
                return JsonResponse(
                    {
                        "status": "Failed",
                        "message": "An error occured while removing the item",
                    }
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid Request"})
    else:
        return JsonResponse({"status": "login_required", "message": "Login Required"})



@login_required(login_url="login")
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def checkout(request):
    addresses = Address.objects.filter(user=request.user)
    cart_count = get_cart_count(request)['cart_count']
    if cart_count <= 0:
        return redirect("cart")
    context = {
        'addresses': addresses,
    }
    return render(request, "marketplace/checkout.html", context)