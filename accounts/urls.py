from django.urls import path
from . import views

urlpatterns = [
    path('register/User/', views.register_user, name='registerUser'),
    path('register/Vendor/', views.register_vendor, name='registerVendor'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('my-account/', views.my_account, name='myAccount'),
    path('customer/Dashboard/', views.customer_dashboard, name='customerDashboard'),
    path('vendor/Dashboard/', views.vendor_dashboard, name='vendorDashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
