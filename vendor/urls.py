from django.urls import path
from accounts import views as AccountViews

from . import views

urlpatterns = [
    path('', AccountViews.vendor_dashboard, name='vendor'),
    path("profile/", views.vendor_profile, name="vendorProfile"),
    path("menu-builder/", views.vendor_menu_builder, name="vendorMenuBuilder"),
    path("menu-builder/sub-category/<slug:slug>/all/", views.vendor_fooditems_category, name="vendorFoodItemsCategory"),

    #category CRUD
    path("menu-builder/sub-category/add/", views.vendor_add_category, name="vendorAddCategory"),
    path("menu-builder/sub-category/<slug:slug>/edit/", views.vendor_edit_category, name="vendorEditCategory"),
]
