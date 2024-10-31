from django.urls import path


from . import views

urlpatterns = [
    path('', views.vendor_dashboard, name='vendor'),
    path("dashboard/", views.vendor_dashboard, name="vendorDashboard"),
    path("profile/", views.vendor_profile, name="vendorProfile"),
    path("menu-builder/", views.vendor_menu_builder, name="vendorMenuBuilder"),
    path("menu-builder/sub-category/<slug:slug>/all/", views.vendor_fooditems_category, name="vendorFoodItemsCategory"),

    # category CRUD
    path("menu-builder/sub-category/add/", views.vendor_add_category, name="vendorAddCategory"),
    path("menu-builder/sub-category/<slug:slug>/edit/", views.vendor_edit_category, name="vendorEditCategory"),

    # Food Item CRUD
    path("menu-builder/food/add/", views.vendor_add_food, name="vendorAddFood"),
    path("menu-builder/food/<slug:slug>/edit/", views.vendor_edit_food, name="vendorEditFood"),
    path("menu-builder/food/<slug:slug>/details/", views.vendor_food_details, name="vendorFoodDetails"),


    # orders
    path("orders/all/", views.vendor_orders_all, name="vendorOrdersAll"),
    path("orders/update-status/", views.vendor_update_order_status, name="vendorUpdateStatus"),
    path("orders/<str:order_number>/details/", views.vendor_my_order_details, name="vendorMyOrderDetails"),
]
