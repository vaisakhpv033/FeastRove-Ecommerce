from django.utils import timezone
from .models import Order
from django.http import HttpResponseBadRequest
import requests
from feastrove.settings import API_KEY
from decimal import Decimal, ROUND_HALF_UP

def generate_order_number(pk):
    current_datetime = timezone.now().strftime('%y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number

def save_order_details(request, address, cart_totals):
    if request.method == 'POST':
        payment_method = request.POST.get('payment-method')
        if not payment_method:
            return HttpResponseBadRequest("payment method is required")
        
        order = Order(
                user=request.user,
                full_name=address.full_name,
                email=request.user.email,
                phone_number=address.phone_number,
                pincode = address.pincode,
                state = address.state.name,
                city = address.city,
                address = address.address,
                total = cart_totals['subtotal'],
                total_tax = cart_totals['tax'],
                payment_method = payment_method,
            )
        order.save()
        order.order_number = generate_order_number(order.id)
        order.save()
        return order
    else:
        return None
    


def inr_to_usd(grand_total: Decimal) -> Decimal:
    api_url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
    # send a get request
    response = requests.get(api_url)

    if response.status_code == 200:
        exchange_data = response.json()
        value = Decimal(str(exchange_data['conversion_rates']['INR']))
        usd_value = grand_total/value
        rounded_value = usd_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return rounded_value
    else:
        print("something went wrong")


