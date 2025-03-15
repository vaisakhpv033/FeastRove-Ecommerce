from django.core.validators import RegexValidator
from django.db import models

from accounts.models import User
from menu.models import FoodItem


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.name


mobile_number_validator = RegexValidator(
    regex=r"^[6-9]\d{9}$", message="Enter a Valid phone number"
)

pincode_validator = RegexValidator(regex=r"^\d{6}$", message="Enter a valid pincode")


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, validators=[mobile_number_validator])
    pincode = models.CharField(max_length=6, validators=[pincode_validator])
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    city = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    road_name = models.CharField(max_length=100)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        else:
            if not Address.objects.filter(user=self.user, is_default=True).exists():
                self.is_default = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user = self.user
        is_default_deleted = self.is_default
        super().delete(*args, **kwargs)

        if is_default_deleted:
            other_address = Address.objects.filter(user=user).first()
            if other_address:
                other_address.is_default = True
                other_address.save()

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Addresses"


class Favourites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fooditem}"

    class Meta:
        unique_together = ("user", "fooditem")
