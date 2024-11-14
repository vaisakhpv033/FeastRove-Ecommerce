from django.db import models
from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor
from customers.models import mobile_number_validator, pincode_validator
from django.core.validators import MaxValueValidator
from menu.validators import validate_positive_price
from coupons_offers.models import Coupons
from decimal import Decimal
from django.core.exceptions import ValidationError

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('Paypal', 'Paypal'),
        ('Razorpay', 'Razorpay'),
        ('COD', 'COD'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=25)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.transaction_id
    

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, null=True, blank=True)
    coupon = models.ForeignKey(Coupons, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    phone_number = models.CharField(max_length=10, validators=[mobile_number_validator])
    pincode = models.CharField(max_length=6, validators=[pincode_validator])
    state = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    country = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False) # when payment successful set to true

    tax_data = models.JSONField(blank=True, null=True, help_text="Data format: {'tax_type': {'tax_percentage': 'tax_amount'}}")
    total_data = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.order_number
    

    def apply_coupon(self, user, coupon):
        """ Apply discount to the order based on the coupon """
        if self.total < coupon.min_order_value:
            raise ValidationError("Doesn't satisfy the minimum amount criteria")
        
        if coupon and coupon.validate_limits(user):
            if coupon.discount_type == 'percentage':
                self.discount_amount = min(
                    (self.total * coupon.discount_amount / Decimal(100)).quantize(Decimal("0.01")), 
                    coupon.max_discount or Decimal("0")
                )
            elif coupon.discount_type =='fixed':
                self.discount_amount = min(coupon.discount_amount, self.total)
            
        return self.save()

    

    def save(self, *args, **kwargs):
        """refund the amount to the wallet of the user if order status is cancelled and the payment method is not COD"""
        if self.pk is not None:
            current = Order.objects.get(pk=self.pk)
            if current.status != self.status and self.status == 'Cancelled' and self.payment_method in ['razorpay', 'paypal']:
                super().save(*args, **kwargs)
                from wallets.models import Wallet # to avoid circular import 
                user_wallet = Wallet.objects.get(user=self.user)
                user_wallet.refund(amount = self.total_amount, order = self, description="Refund completed")
                return
        return super().save(*args, **kwargs)

    
    @property
    def total_amount(self):
        return (self.total + self.total_tax - self.discount_amount) if self.discount_amount else (self.total + self.total_tax)
    
    @property
    def vendor_total_amount(self):
        return self.total + self.total_tax
    
    


class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_foods")
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(
        validators=[MaxValueValidator(5, "Maximum allowed quantity is 5")]
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_positive_price]
    )
    
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem.food_title


    @property
    def total_amount(self):
        return self.quantity * self.price
