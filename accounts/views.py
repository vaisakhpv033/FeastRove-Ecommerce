from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from accounts.utils import detect_user, check_role_customer, check_role_vendor, send_verification_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseBadRequest



# Create your views here.
def register_user(request):
    if request.user.is_authenticated:
        return redirect('myaccount')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name, 
                last_name=last_name,
                username=username,
                email=email,
                password=password 
            )
            user.role = User.CUSTOMER
            user.save()

            # send verification email
            send_verification_email(request, user)

            messages.success(request, "A verification link has been sent to your email." )
            return redirect('registerUser')
    else:
        form = UserForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/registerUser.html', context)


def register_vendor(request):
    if request.user.is_authenticated:
        return redirect('myaccount')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendor_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name, 
                last_name=last_name,
                username=username,
                email=email,
                password=password 
            )
            user.role = User.VENDOR
            user.save()
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # send verification email
            send_verification_email(request, user)

            messages.success(request, "A verification link has been sent to your email.")
            return redirect('registerVendor')
        else:
            print(form.errors, vendor_form.errors, end='\n')
    else:
        form = UserForm()
        vendor_form = VendorForm()
    
    context = {
        'form': form,
        'vendor_form': vendor_form,
    }
    return render(request, 'accounts/registerVendor.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations Your account is activated')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return HttpResponseBadRequest(render(request, '400.html'))


def login(request):
    if request.user.is_authenticated:
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('myAccount')
        else: 
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')



def logout(request):
    auth.logout(request)
    messages.info(request, "you are successfully logged out")
    return redirect('login')

@login_required(login_url='login')
def my_account(request):
    user = request.user
    redirect_url = detect_user(user)
    return redirect(redirect_url)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customer_dashboard(request):
    return render(request, 'accounts/customerDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    return render(request, 'accounts/vendorDashboard.html')
