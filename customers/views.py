from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import cache_control
from accounts.models import UserProfile
from accounts.forms import UserProfileForm
from accounts.utils import check_role_customer

# Create your views here.

@login_required(login_url="login")
@user_passes_test(check_role_customer)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('customerProfile')
    else:
        profile_form = UserProfileForm(instance=profile)
    context = {
        'profile': profile,
        'profile_form': profile_form,
    }
    return render(request, "customer/profile.html", context)