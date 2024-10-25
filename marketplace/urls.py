from django.urls import path
from .import views
from customers import views as Customerviews

urlpatterns = [
    path('', views.marketplace, name="marketplace"),
    path('<slug:vendor_slug>/all-categories/', views.restaurant_details, name="restaurantDetails"),
    path('<slug:vendor_slug>/<slug:category_slug>/all/', views.restaurant_details, name="restaurantCategoryDetails"),
    path('<slug:slug>/details/', views.food_item_details, name="foodItemDetails"),

    path('cart/', views.cart, name='cart'),
    # Add to Cart
    path('cart/<slug:slug>/add', views.add_to_cart, name="addToCart"),
    path('cart/<slug:slug>/decrease', views.decrease_from_cart, name="decreaseFromCart"),

    path('cart/<int:cart_id>/remove-item', views.remove_cart_item, name="removeCartItem" ),

    path('checkout/', views.checkout, name="checkout"),
    path('checkout/addresses/add/', Customerviews.customer_add_address, name="checkoutAddAddress"),

    path('search/', views.search, name="search"),
    
]
