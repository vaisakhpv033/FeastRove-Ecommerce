from django.core.validators import MaxValueValidator
from django.db import models

from accounts.models import User
from menu.models import FoodItem


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        validators=[MaxValueValidator(5, "Maximum allowed quantity is 5")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.fooditem.price * self.quantity

    def __str__(self):
        return f"{self.user.username}-{self.fooditem}-Qty-{self.quantity}"



class Tax(models.Model):
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Tax Percentage (%)")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Taxes"
    def __str__(self):
        return self.tax_type