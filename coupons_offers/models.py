from django.db import models
from django.utils import timezone
from vendor.models import Vendor
from django.core.exceptions import ValidationError

# Create your models here.
class Coupons(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ]

    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2) # % if percentage else fixed amount
    max_discount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Maximum discount amount for percentage type coupons")
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="minimum order value to apply the coupon")
    start_date = models.DateTimeField(default = timezone.now)
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="maximun no of times this coupon can be used by all the users")
    user_limit = models.PositiveIntegerField(null=True, blank=True, help_text="maximum no of times each user can use this coupon")
    is_active = models.BooleanField(default=False)
    vendor = models.ManyToManyField(Vendor, blank=True, help_text="If specified the coupon is valid only for these vendors")
    description = models.TextField(blank=True, help_text="optional description for the coupon")

    def __str__(self):
        return self.code
    
    def is_valid(self):
        """ Check if the coupon is active and within the specified date range """
        now = timezone.now()
        return self.is_active and (self.start_date <= now <= self.end_date)
    

    def validate_limits(self, user):
        """ Validate user limit and usage limit for the coupon """
        if not self.is_valid():
            raise ValidationError("This coupon is no longer active or expired")
        
        # check total usage limits
        from orders.models import Order
        total_usage = Order.objects.filter(coupon=self, order_number__isnull=False).count()
        if self.usage_limit and total_usage >= self.usage_limit:
            raise ValidationError("This coupon is no longer active")
        
        # check total user limits
        user_usage = Order.objects.filter(coupon=self, user=user).count()
        if self.user_limit and user_usage >= self.user_limit:
            raise ValidationError("You have reached maximum usage limit for this coupon")
        
        return True
        
    
    class Meta:
        verbose_name_plural = 'Coupons'

