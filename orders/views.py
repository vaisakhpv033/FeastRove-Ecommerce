import razorpay
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_POST

from accounts.utils import check_role_customer, send_notification
from customers.models import Address
from feastrove.settings import RZP_KEY_ID, RZP_KEY_SECRET
from marketplace.context_processors import get_cart_count, get_cart_total
from marketplace.models import Cart
from wallets.models import Wallet, WalletTransaction

from .models import Order, OrderedFood, Payment
from .utils import inr_to_usd, save_order_details, verify_signature
from coupons_offers.models import Coupons

client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))


# Create your views here.
@login_required(login_url="login")
@user_passes_test(check_role_customer)
@require_POST
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def place_order(request):
    address = get_object_or_404(
        Address, user=request.user, pk=request.POST["delivery-address"]
    )
    coupon_code = request.POST["applied_coupon"]
    coupon = None
    if coupon_code:
        coupon = Coupons.objects.get(code=coupon_code)
    cart_count = get_cart_count(request)["cart_count"]
    cart_totals = get_cart_total(request)
    if cart_count <= 0:
        return redirect("home")

    order = save_order_details(request, address=address, cart_totals=cart_totals, coupon=coupon)
    if order:
        cart_items = Cart.objects.filter(user=request.user).order_by("-created_at")

       
        for item in cart_items:
            ordered_food = OrderedFood(
                order=order,
                
                user=request.user,
                fooditem=item.fooditem,
                quantity=item.quantity,
                price=item.fooditem.price,
            )
            ordered_food.save()

        # assigning vendor to the order
        order.vendor = cart_items[0].fooditem.vendor
        order.save()

        # Razorpay
        if order.payment_method == "razorpay":
            amount = int(order.total_amount * 100)
            data = {
                "amount": amount,
                "currency": "INR",
                "receipt": "RZP" + order.order_number,
            }
            payment = client.order.create(data=data)
            rzp_order_id = payment["id"]

            request.session[order.order_number] = rzp_order_id

            context = {
                "cart_items": cart_items,
                "order": order,
                "address": address,
                "rzp_order_id": rzp_order_id,
                "RZP_KEY_ID": RZP_KEY_ID,
                "amount": amount,
            }
        elif order.payment_method == "paypal":
            usd_amount = inr_to_usd(order.total_amount)
            context = {
                "cart_items": cart_items,
                "order": order,
                "address": address,
                "usd_amount": usd_amount,
            }
        else:
            context = {
                "cart_items": cart_items,
                "order": order,
                "address": address,
            }
        return render(request, "orders/placeOrder.html", context)

    messages.error(request, "Something Went Wrong")
    return redirect(request, "checkout")


@login_required(login_url="login")
@user_passes_test(check_role_customer)
@require_POST
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def payments(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")
        razorpay_signature = request.POST.get("razorpay_signature")

        order_id = request.session.get(order_number)

        # verify the payment through signature generation
        if payment_method == "Razorpay":
            if not verify_signature(order_id, transaction_id, razorpay_signature):
                return JsonResponse(
                    {"error": "Payment Verification Failed"}, status=403
                )

        if not all([order_number, transaction_id, payment_method, status]):
            return JsonResponse({"error": "Invalid Payment details"}, status=400)

        # retrieve the order or return 404 not found
        order = get_object_or_404(Order, user=request.user, order_number=order_number)

        # create and save payment record
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total_amount,
            status=status,
        )
        payment.save()

        # update order status
        order.payment = payment
        order.is_ordered = True
        order.save()

        OrderedFood.objects.filter(order=order).update(payment=payment)

        cart_items = Cart.objects.filter(user=request.user)
        cart_items.delete()

        if order.payment_method == "razorpay":
            del request.session[order_number]

        # # Send order confirmation email to the customer
        # email_subject = "Your Order Placed Successfully"
        # email_template = "orders/order_confirmation_email.html"
        # context = {"user": request.user, "order": order}
        # send_notification(
        #     email_subject=email_subject, email_template=email_template, context=context
        # )

        # # Send order receive email to the vendor
        # email_subject = "A new order has been got"
        # email_template = "orders/new_order_received_email.html"
        # to_emails = [order.vendor.user.email]
        # context = {"user": request.user, "order": order, "to_emails": to_emails}
        # send_notification(
        #     email_subject=email_subject,
        #     email_template=email_template,
        #     context=context,
        #     to_email=to_emails,
        # )
        
        response = {
            "message": "Success",
            "order_number": order_number,
            "transaction_id": transaction_id,
        }
        return JsonResponse(response)
    return JsonResponse({"status": "Failed", "message": "Invalid Request"})


@login_required(login_url="login")
@user_passes_test(check_role_customer)
@require_POST
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def payment_cod_wallet(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        order_number = request.POST.get("order_number")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")

        order = get_object_or_404(Order, user=request.user, order_number=order_number)

        if not all([order_number, payment_method, status]):
            return JsonResponse({"error": "Invalid Payment details"}, status=400)
        
        if payment_method == 'wallet':
            wallet = get_object_or_404(Wallet, user=request.user)
            if order.total_amount > wallet.balance:
                return JsonResponse({'error': "Not enough Balance. Payment failed"}, status=400)
            wallet.withdraw(order.total_amount, description=f"Withdrawal for order: {order.order_number}", order=order)
            wallet_transaction = WalletTransaction.objects.get(wallet=wallet, order=order, transaction_type='WITHDRAW')
            payment = Payment(
                user=request.user,
                transaction_id=wallet_transaction.transaction_no,
                payment_method=payment_method,
                amount=order.total_amount,
                status="COMPLETED",
            )
            payment.save()
            order.payment = payment
            

        # update order status
        order.is_ordered = True
        order.save()
        cart_items = Cart.objects.filter(user=request.user)
        cart_items.delete()

        # # Send order confirmation email to the customer
        # email_subject = "Your Order Placed Successfully"
        # email_template = "orders/order_confirmation_email.html"
        # context = {"user": request.user, "order": order}
        # send_notification(
        #     email_subject=email_subject, email_template=email_template, context=context
        # )

        # # Send order receive email to the vendor
        # email_subject = "A new order has been got"
        # email_template = "orders/new_order_received_email.html"
        # to_emails = [order.vendor.user.email]
        # context = {"user": request.user, "order": order, "to_emails": to_emails}
        # send_notification(
        #     email_subject=email_subject,
        #     email_template=email_template,
        #     context=context,
        #     to_email=list(to_emails),
        # )
       
        response = {
            "message": "Success",
            "order_number": order_number,
        }
        return JsonResponse(response)
    return JsonResponse({"status": "Failed", "message": "Invalid Request"})



@login_required(login_url="login")
@user_passes_test(check_role_customer)
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def order_complete(request):
    order_number = request.GET.get("order-no")
    order = get_object_or_404(Order, user=request.user, order_number=order_number)
    ordered_food = OrderedFood.objects.filter(user=request.user, order=order)
    context = {
        "order": order,
        "ordered_food": ordered_food,
    }
    return render(request, "orders/orderComplete.html", context)
