from django.urls import path
from .import views

urlpatterns = [
    path("", views.admin_dashboard, name="adminDashboard"),
    path("customers/list/", views.admin_customer_data, name="adminCustomerData"),
    path("vendor/list/", views.admin_vendor_data, name="adminVendorData"),
    path("vendor/approve/", views.admin_vendor_approve, name="adminVendorApprove"),
    path("vendor/details/<slug:slug>/", views.VendorDetailView.as_view(), name="adminVendorDetails"),
    path("customer/details/<int:user_id>/", views.CustomerDetailView.as_view(), name="adminCustomerDetails"),


    path('vendor/<slug:slug>/approve/', views.approve_vendor, name='adminApproveVendor'),
    path('vendor/<slug:slug>/disapprove/', views.disapprove_vendor, name='adminDisapproveVendor'),
]
