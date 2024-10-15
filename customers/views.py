from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_control

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.utils import check_role_customer, validate_password

from .forms import AddressForm
from .models import Address


# Create your views here.


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
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully")
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
def customer_delete_address(request, address_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            address = get_object_or_404(Address, pk=address_id, user=request.user)
            address.delete()
            return JsonResponse({'status': 'Success', 'message': 'Address deleted successfully'})
        except Address.DoesNotExist:
            return JsonResponse({'status': 'Failed', 'message': 'Address does not exist'})
    return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
