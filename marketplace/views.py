from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # 'D' is Shortcut for Distance
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control

from accounts.utils import check_role_customer
from customers.models import Address
from menu.models import Category, FoodItem
from vendor.models import Vendor

from .context_processors import get_cart_count, get_cart_total
from .models import Cart

# Create your views here.


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
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
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def cart(request):
    cart_items = Cart.objects.filter(
        user=request.user, fooditem__is_available=True
    ).order_by("-created_at")
    # remove unavailable items from the cart
    Cart.objects.filter(user=request.user, fooditem__is_available=False).delete()
    context = {
        "cart_items": cart_items,
    }
    return render(request, "marketplace/cart.html", context)


def add_to_cart(request, slug):
    if request.user.is_authenticated:
        if (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            and request.user.role == 2
        ):
            # Check if the fooditem exists
            try:
                fooditem = FoodItem.objects.get(slug=slug, is_available=True)
                vendor = fooditem.vendor

                cart_items = Cart.objects.filter(user=request.user)
                if cart_items.exists():
                    # get the vendor of the items in the current cart
                    current_vendor = cart_items.first().fooditem.vendor

                    # if the vendors are different delete the cart items
                    if current_vendor != vendor:
                        cart_items.delete()

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
                    {"status": "Failed", "message": "Item Currently Unavailable!"}
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
        if (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            and request.user.role == 2
        ):
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
        if (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            and request.user.role == 2
        ):
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
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def checkout(request):
    addresses = Address.objects.filter(user=request.user)
    # remove unavailable items from the cart
    Cart.objects.filter(user=request.user, fooditem__is_available=False).delete()
    cart_count = get_cart_count(request)["cart_count"]
    if cart_count <= 0:
        messages.error(request, "Item Currently Unavailable")
        return redirect("cart")
    context = {
        "addresses": addresses,
    }
    return render(request, "marketplace/checkout.html", context)


# Search Page
def search(request):
    if "location" not in request.GET or "radius" not in request.GET:
        return redirect("home")
    address = request.GET["location"]
    latitude = request.GET["latitude"]
    longitude = request.GET["longitude"]
    radius = request.GET["radius"]
    keyword = request.GET["rest_food"]

    # fetch vendors by food id
    fetch_vendor_lst = (
        FoodItem.objects.filter(food_title__icontains=keyword, is_available=True)
        .values_list("vendor", flat=True)
        .distinct()
    )

    # if lat and lng present query vendors based on the nearest distance from the address provided
    if latitude and longitude:
        pnt = GEOSGeometry("POINT(%s %s)" % (longitude, latitude))
        vendors = (
            Vendor.objects.filter(
                (Q(id__in=fetch_vendor_lst) | Q(vendor_name__icontains=keyword)),
                is_approved=True,
                user__is_active=True,
                user_profile__location__distance_lte=(pnt, D(km=radius)),
            )
            .annotate(distance=Distance("user_profile__location", pnt))
            .order_by("distance")
        )

    else:
        vendors = Vendor.objects.filter(
            (Q(id__in=fetch_vendor_lst) | Q(vendor_name__icontains=keyword)),
            is_approved=True,
            user__is_active=True,
        )

    context = {"restaurants": vendors, "address": address}
    return render(request, "marketplace/restaurantListing.html", context)
