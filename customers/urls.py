from django.urls import path

from accounts import views as Accountviews

from . import views

urlpatterns = [
    path("", Accountviews.customer_dashboard, name="customer"),
    path("profile/", views.customer_profile, name="customerProfile"),
    path("addresses/", views.customer_addresses, name="customerAddresses"),
    path("addresses/add/", views.customer_add_address, name="customerAddAddress"),
    path("addresses/<int:address_id>/edit/", views.customer_edit_address, name="customerEditAddress"),
    path("addresses/<int:address_id>/delete/", views.customer_delete_address, name="customerDeleteAddress"),
    path("reset-password/", views.customer_reset_password, name="customerResetPassword"),
]
