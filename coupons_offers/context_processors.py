from marketplace.context_processors import get_cart_total
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError

def get_discounted_total(request, coupon):
    cart_total = get_cart_total(request)
    if cart_total['subtotal'] >= coupon.min_order_value:
        if coupon.discount_type == 'percentage':
            discount_amount = min(
                (cart_total['subtotal'] * coupon.discount_amount / Decimal(100)).quantize(Decimal("0.01")),
                coupon.max_discount or Decimal("0")
            )
        elif coupon.discount_type == 'fixed':
            discount_amount = min(coupon.discount_amount, cart_total['subtotal'])

        discount_subtotal = cart_total['subtotal'] - discount_amount
        discount_grand_total = (discount_subtotal + cart_total['tax']).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        discount_cart_total = {
            'discount_subtotal': discount_subtotal,
            'discount_grand_total': discount_grand_total,
            'discount': discount_amount
        }
        return discount_cart_total
    else:
        raise ValidationError(f"minimum order value is {coupon.min_order_value}")

