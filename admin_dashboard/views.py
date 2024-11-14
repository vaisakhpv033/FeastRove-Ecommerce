from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from accounts.models import User
from vendor.models import Vendor
from orders.models import Order
from .utils import customer_count, top_10_products

# Create your views here.
@user_passes_test(lambda u: u.is_superadmin, login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    orders = Order.objects.filter(is_ordered=True).order_by('created_at')
    customer_data = customer_count()
    top_products = top_10_products()
    context = {
        'orders': orders,
        'customer_data': customer_data,
        'top_products': top_products
    }
    return render(request, "admin_dashboard/adminDashboard.html", context)



@user_passes_test(lambda user: user.is_superadmin, login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_customer_data(request):
    customers = User.objects.filter(Q(role=User.CUSTOMER) & Q(is_active=True)).order_by("-date_joined")
    return render(request, "admin_dashboard/adminCustomerData.html", {"users": customers})




@user_passes_test(lambda user: user.is_superadmin, login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_vendor_data(request):
    vendors = Vendor.objects.select_related('user').filter(is_approved=True).order_by("-created_at")
    for i in vendors:
        print(i.vendor_name)
        print(i.user.first_name)
    return render(request, "admin_dashboard/adminVendorData.html", {"users": vendors})



@user_passes_test(lambda user: user.is_superadmin, login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_vendor_approve(request):
    vendors = Vendor.objects.select_related('user').filter(is_approved=False).order_by("-created_at")
    return render(request, "admin_dashboard/adminVendorApprove.html", {"users": vendors})


@method_decorator(
    user_passes_test(lambda u: u.is_superadmin, login_url="login"), name="dispatch"
)
@method_decorator(
    cache_control(no_cache=True, must_revalidate=True, no_store=True), name="dispatch"
)
class VendorDetailView(DetailView):
    model = Vendor
    template_name = 'admin_dashboard/adminVendorDetails.html'
    context_object_name = 'vendor'
    slug_field = 'vendor_slug'  
    slug_url_kwarg = 'slug'    




@method_decorator(
    user_passes_test(lambda u: u.is_superadmin, login_url="login"), name="dispatch"
)
@method_decorator(
    cache_control(no_cache=True, must_revalidate=True, no_store=True), name="dispatch"
)
class CustomerDetailView(DetailView):
    model = User
    template_name = 'admin_dashboard/adminCustomerDetails.html'
    context_object_name = 'user'  
    pk_url_kwarg = "user_id"   




def check_role_admin(user):
    return user.is_superadmin


@login_required(login_url='login')
@user_passes_test(check_role_admin)
@require_POST
def approve_vendor(request, slug):
    vendor = get_object_or_404(Vendor, vendor_slug=slug)
    vendor.is_approved = True
    vendor.save()
    messages.success(request, f"{vendor.vendor_name} has been approved.")
    return redirect(reverse('adminVendorDetails', kwargs={'slug': slug}))


@login_required(login_url='login')
@user_passes_test(check_role_admin)
@require_POST
def disapprove_vendor(request, slug):
    vendor = get_object_or_404(Vendor, vendor_slug=slug)
    vendor.is_approved = False
    vendor.save()
    messages.success(request, f"{vendor.vendor_name} has been disapproved.")
    return redirect(reverse('adminVendorDetails', kwargs={'slug': slug}))



