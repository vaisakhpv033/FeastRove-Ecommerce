from django.urls import path
from .import views

urlpatterns = [
    path("review-vendor/", views.vendor_review, name="reviewVendor"),
]