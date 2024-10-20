from django.shortcuts import render, redirect, get_object_or_404
from marketplace.context_processors import get_cart_count
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_POST
from .utils import save_order_details, inr_to_usd
from django.http import HttpResponse, JsonResponse
from customers.models import Address
from marketplace.models import Cart
from .models import Payment, Order, OrderedFood
from django.contrib import messages
from feastrove.settings import RZP_KEY_ID, RZP_KEY_SECRET
from accounts.utils import send_notification
from marketplace.context_processors import get_cart_total
import razorpay

client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

# Create your views here.
@login_required
@require_POST
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def place_order(request):
    address = get_object_or_404(Address, user=request.user, pk=request.POST['delivery-address'])
    cart_count = get_cart_count(request)['cart_count']
    cart_totals = get_cart_total(request)
    if cart_count <= 0:
        return redirect("home")
    
    order = save_order_details(request, address=address, cart_totals=cart_totals)
    if order:
        cart_items = Cart.objects.filter(user=request.user).order_by('-created_at')

        # Razorpay
        if order.payment_method == 'razorpay':
            amount = int(cart_totals['grand_total'] * 100)
            data = { 
                "amount": amount,
                "currency": "INR", 
                "receipt": "RZP"+order.order_number 
            }
            payment = client.order.create(data=data)
            rzp_order_id = payment['id']

            context = {
                'cart_items': cart_items,
                'order': order,
                'address': address,
                'rzp_order_id': rzp_order_id,
                'RZP_KEY_ID': RZP_KEY_ID,
                'amount': amount,
            }
        else:
            usd_amount = inr_to_usd(cart_totals['grand_total']) 
            context = {
                'cart_items': cart_items,
                'order': order,
                'address': address,
                'usd_amount': usd_amount,
            }
        return render(request, "orders/PlaceOrder.html", context)
    
    messages.error(request, "Something Went Wrong")
    return redirect(request, "checkout")


@login_required
@require_POST
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def payments(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        
        if not all([order_number, transaction_id, payment_method, status]):
            return JsonResponse({'error': "Invalid Payment details"}, status=400)
        
        # retrieve the order or return 404 not found
        order = get_object_or_404(Order, user=request.user, order_number=order_number)

        # create and save payment record
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()

        # update order status
        order.payment = payment
        order.is_ordered = True
        order.save()


        # move the cart items to ordered food items
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood(
                order = order,
                payment = payment,
                user = request.user,
                fooditem = item.fooditem,
                quantity = item.quantity,
                price = item.fooditem.price
            )
            ordered_food.save()
        
        # Send order confirmation email to the customer
        email_subject = "Your Order Placed Successfully"
        email_template = "orders/order_confirmation_email.html"
        context = {
            'user': request.user,
            'order': order
        }
        send_notification(email_subject=email_subject, email_template=email_template, context=context)


        # Send order receive email to the vendor
        email_subject = "A new order has been got"
        email_template = "orders/new_order_received_email.html"
        to_emails = set(item.fooditem.vendor.user.email for item in cart_items)
        context = {
            'user': request.user,
            'order': order,
            'to_emails': to_emails
        }
        send_notification(email_subject=email_subject, email_template=email_template, context=context, to_email=list(to_emails)) 
        cart_items.delete()
        response = {
            'message': "Success",
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse('Payments View')



def order_complete(request):
    order_number = request.GET.get('order-no')
    transaction_id = request.GET.get('trans-id')
    return render(request, 'orders/OrderComplete.html')