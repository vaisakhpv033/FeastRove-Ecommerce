from django.urls import path

from accounts import views as Accountviews

from . import views

urlpatterns = [
    path("", Accountviews.customer_dashboard, name="customer"),
    path("profile/", views.customer_profile, name="customerProfile"),
]
