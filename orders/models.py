from django.db import models
from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor
from customers.models import mobile_number_validator, pincode_validator, State
from django.core.validators import MaxValueValidator
from menu.validators import validate_positive_price

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('Paypal', 'Paypal'),
        ('Razorpay', 'Razorpay'),
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
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    phone_number = models.CharField(max_length=10, validators=[mobile_number_validator])
    pincode = models.CharField(max_length=6, validators=[pincode_validator])
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    city = models.CharField(max_length=30)
    country = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)

    tax_data = models.JSONField(blank=True, null=True, help_text="Data format: {'tax_type': {'tax_percentage': 'tax_amount'}}")
    total_data = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.order_number
    


class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        validators=[MaxValueValidator(5, "Maximum allowed quantity is 5")]
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_positive_price]
    )
    amount = models.DecimalField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem.food_title
    

    @property
    def total_amount(self):
        return self.quantity * self.price
