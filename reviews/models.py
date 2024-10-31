from django.db import models

from accounts.models import User
from orders.models import Order


# Create your models here.
class VendorReview(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="order_reviews"
    )
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="order_review"
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.email
