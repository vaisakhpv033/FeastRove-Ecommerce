from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.utils import check_role_customer
from .models import Coupons
from django.core.exceptions import ValidationError
from .context_processors import get_discounted_total

# Create your views here.
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def verify_coupon(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        coupon = request.GET.get('coupon_code')
        print(coupon)
        try:
            coupon = Coupons.objects.get(code=coupon, is_active=True)
            coupon.validate_limits(request.user)
            discounted_total = get_discounted_total(request, coupon)
            print(discounted_total)
            return JsonResponse({'status': 'Success', 'message': 'Coupon Available', 'discounted_total': discounted_total}, status=200)
        except Coupons.DoesNotExist:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Coupon'})
        except ValidationError as e:
            return JsonResponse({'status': 'Failed', 'message': list(e)})
    else:
        return JsonResponse({'status':'Failed', 'message': "Invalid Request"}, status=400)