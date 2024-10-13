from .models import Cart
from django.db.models import Sum, F
from decimal import Decimal, ROUND_HALF_UP

def get_cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_count = Cart.objects.filter(user=request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0
            
        except Cart.DoesNotExist:
            cart_count = 0
            
    return {'cart_count': cart_count}


def get_cart_total(request):
    subtotal = Decimal(0.00)
    tax_rate = Decimal(0.05)
    tax = Decimal(0.00)
    grand_total = Decimal(0.00) 
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).select_related('fooditem')
        
        subtotal = cart_items.aggregate(subtotal=Sum(F('fooditem__price') * F('quantity')))['subtotal'] or Decimal('0.00')   

        tax = (subtotal * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        grand_total = (subtotal + tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    
    return {'subtotal': subtotal, 'tax': tax, 'grand_total': grand_total}
