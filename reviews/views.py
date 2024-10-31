from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.utils import check_role_customer
from orders.models import Order

from .models import VendorReview


# Create your views here.
@login_required(login_url="login")
@user_passes_test(check_role_customer)
@require_POST
def vendor_review(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        order_number = request.POST.get("order_number")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        order = Order.objects.get(user=request.user, order_number=order_number)
        if not all([order_number, rating, order]):
            return JsonResponse({"status": "Failed", "message": "Invalid Request"})

        VendorReview.objects.create(
            user=request.user, order=order, rating=rating, comment=comment
        )
        return JsonResponse({"status": "Success", "message": "Added Your rating"})
    else:
        return JsonResponse({"status": "Failed", "message": "Invalid Request"})
