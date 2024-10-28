from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_control

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.utils import check_role_customer, validate_password
from menu.models import FoodItem

from .forms import AddressForm
from .models import Address, Favourites
from orders.models import Order, OrderedFood
from wallets.models import Wallet, WalletTransaction



@login_required(login_url="login")
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect("customerProfile")
    else:
        profile_form = UserProfileForm(instance=profile)
    context = {
        "profile": profile,
        "profile_form": profile_form,
    }
    return render(request, "customer/profile.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            try:
                user = request.user
                validate_password(password)
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password resetted successfully")
                return redirect("myAccount")
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return redirect("customerResetPassword")
        else:
            messages.error(request, "passwords doesn't match")
    return render(request, "customer/resetPassword.html")


@login_required(login_url="login")
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_addresses(request):
    addresses = Address.objects.filter(user=request.user)

    context = {
        "addresses": addresses,
    }
    return render(request, "customer/customerAddresses.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_add_address(request):
    form = AddressForm()
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            def_address = Address.objects.filter(user=request.user)
            if not def_address:
                address.is_default = True
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully")
            if "checkout/" in request.path:
                return redirect("checkout")
            return redirect("customerAddresses")
    context = {
        "form": form,
    }
    return render(request, "customer/customerAddAddress.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_edit_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id, user=request.user)
    form = AddressForm(instance=address)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address Updated Successfully")
            return redirect("customerAddresses")
    context = {
        "form": form,
        "address": address,
    }
    return render(request, "customer/customerEditAddress.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_delete_address(request, address_id):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            address = get_object_or_404(Address, pk=address_id, user=request.user)
            address.delete()
            return JsonResponse(
                {"status": "Success", "message": "Address deleted successfully"}
            )
        except Address.DoesNotExist:
            return JsonResponse(
                {"status": "Failed", "message": "Address does not exist"}
            )
    return JsonResponse({"status": "Failed", "message": "Invalid request"})

@login_required(login_url="login")
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_favourites(request):
    fav_items = Favourites.objects.filter(user=request.user).order_by("-created_at")
    context = {
        "fav_items": fav_items,
    }
    return render(request, "customer/favourites.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_add_fav_item(request, food_item_slug):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            food_item = FoodItem.objects.get(slug=food_item_slug)
            if Favourites.objects.filter(
                user=request.user, fooditem=food_item
            ).exists():
                return JsonResponse(
                    {"status": "Failed", "message": "Already in favourites"}
                )
            fav_item = Favourites(user=request.user, fooditem=food_item)
            fav_item.save()
            return JsonResponse({"status": "Success", "message": "Added To Favourites"})
        except FoodItem.DoesNotExist:
            return JsonResponse(
                {"status": "Failed", "message": "FoodItem Does Not exist"}
            )
        except IntegrityError:
            return JsonResponse(
                {
                    "status": "Failed",
                    "message": "Database error, Please try again after sometime",
                }
            )
        except Exception:
            return JsonResponse({"status": "Failed", "message": "something went Wrong"})
    else:
        return JsonResponse({"status": "Failed", "message": "Invalid Request"})


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_remove_fav_item(request, fav_item_id):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            fav_item = Favourites.objects.get(pk=fav_item_id, user=request.user)
            fav_item.delete()
            return JsonResponse(
                {"status": "Success", "message": "Removed from favourites"}
            )
        except Favourites.DoesNotExist:
            return JsonResponse({"status": "Failed", "message": "Item Does not Exist"})
    else:
        return JsonResponse({"status": "Failed", "message": "Invalid Request"})


@login_required(login_url='login')
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders
    }
    return render(request, "customer/customerMyOrders.html", context)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_my_order_details(request, order_number):
    order = get_object_or_404(Order, user=request.user, order_number=order_number, is_ordered=True)
    order_items = OrderedFood.objects.filter(user=request.user, order=order)

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, "customer/customerMyOrderDetails.html", context)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    wallet_transactions = WalletTransaction.objects.filter(wallet=wallet)
    context = {
        'wallet': wallet,
        'transactions': wallet_transactions,
    }
    return render(request, "customer/customerMyWallet.html", context)