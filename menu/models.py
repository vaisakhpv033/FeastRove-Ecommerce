import os
from django.db import models
from vendor.models import Vendor
from django.utils.text import slugify
from accounts.validators import validate_file_mimetype
from .validators import validate_positive_price

# To construct dynamic path
def food_image_upload_path(instance, filename):
    vendor_name = slugify(instance.vendor.vendor_name) 
    category_name = slugify(instance.category.category_name)
    food_title = slugify(instance.food_title)
    
    return os.path.join('foodimages', vendor_name, category_name, food_title, filename)

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def clean(self):
        self.category_name = self.category_name.capitalize()

    def __str__(self):
        return self.category_name
    

class FoodItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    food_title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive_price])
    image = models.ImageField(upload_to=food_image_upload_path, validators=[validate_file_mimetype])
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_title
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.food_title)
        super().save(*args, **kwargs)
