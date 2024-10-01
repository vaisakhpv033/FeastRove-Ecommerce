from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import cache_control

from accounts.utils import (
    check_role_customer,
    check_role_vendor,
    detect_user,
    send_verification_email,
    validate_password,
)
from vendor.forms import VendorForm

from .forms import UserForm
from .models import User, UserProfile


# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def register_user(request):
    if request.user.is_authenticated:
        return redirect("myaccount")
    elif request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.CUSTOMER
            user.save()

            # send verification email
            mail_subject = "Activate your account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_email(
                request, user, email_subject=mail_subject, email_template=email_template
            )

            messages.success(
                request, "A verification link has been sent to your email."
            )
            return redirect("registerUser")
    else:
        form = UserForm()
    context = {"form": form}
    return render(request, "accounts/registerUser.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def register_vendor(request):
    if request.user.is_authenticated:
        return redirect("myaccount")
    elif request.method == "POST":
        form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendor_form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.VENDOR
            user.save()
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # send verification email
            mail_subject = "Activate your account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_email(
                request, user, email_subject=mail_subject, email_template=email_template
            )

            messages.success(
                request, "A verification link has been sent to your email."
            )
            return redirect("registerVendor")
        else:
            print(form.errors, vendor_form.errors, end="\n")
    else:
        form = UserForm()
        vendor_form = VendorForm()

    context = {
        "form": form,
        "vendor_form": vendor_form,
    }
    return render(request, "accounts/registerVendor.html", context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations Your account is activated")
        return redirect("myAccount")
    else:
        messages.error(request, "Invalid activation link")
        return HttpResponseBadRequest(render(request, "400.html"))


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.user.is_authenticated:
        return redirect("myAccount")
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("myAccount")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")
    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.info(request, "you are successfully logged out")
    return redirect("login")


@login_required(login_url="login")
def my_account(request):
    user = request.user
    redirect_url = detect_user(user)
    return redirect(redirect_url)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_dashboard(request):
    return render(request, "accounts/customerDashboard.html")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    return render(request, "accounts/vendorDashboard.html")


# Forgot password
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("myAccount")
    if request.method == "POST":
        email = request.POST["email"]

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = "Reset Your Password"
            email_template = "accounts/emails/reset_password_email.html"
            send_verification_email(
                request, user, email_subject=mail_subject, email_template=email_template
            )

            messages.success(request, "Password reset link has been sent to your email address")
            return redirect("login")
        else:
            messages.error(request, "Account does not exist")
            return redirect("forgotPassword")

    return render(request, "accounts/forgotPassword.html")


# validate the reset password link
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.info(request, "Reset Your Password")
        return redirect("resetPassword")
    else:
        messages.error(request, "Invalid reset password link")
        return HttpResponseBadRequest(render(request, "400.html"))


# resetting the password
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reset_password(request):
    if not request.session.get("uid"):
        return HttpResponseBadRequest()
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            try:
                pk = request.session.get("uid")
                user = User.objects.get(pk=pk)
                validate_password(password)
                user.set_password(password)
                user.is_active = True
                user.save()
                messages.success(request, "Password resetted successfully")
                request.session.pop("uid", None)
                return redirect("login")
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return redirect("resetPassword")
        else:
            messages.error(request, "Password do not match")
            return redirect("resetPassword")
    return render(request, "accounts/resetPassword.html")
