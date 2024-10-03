from django.shortcuts import render
from django.db.models import Q
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from accounts.models import User
from vendor.models import Vendor

# Create your views here.
@user_passes_test(lambda u: u.is_superadmin, login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    return render(request, "admin_dashboard/adminDashboard.html")



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
