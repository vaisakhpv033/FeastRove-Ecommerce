from django.urls import path
from .import views



urlpatterns = [
    path('place-order/', views.place_order, name="placeOrder"),
    path('payments/', views.payments, name="payments"),
    path('payments-cod/', views.payment_cod_wallet, name="paymentsCod"),
    path('order-complete/', views.order_complete, name="orderComplete"),
]
