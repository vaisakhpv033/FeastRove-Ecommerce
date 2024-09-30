from django.db import models 
from accounts.models import User, UserProfile
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import magic


def validate_file_mimetype(file):
    try:
        file_mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # Reset the file pointer after reading
    except magic.MagicException:
        print("file can't read")
        raise ValidationError("Error occurred while reading the file.")
    
    accept = ['image/png', 'image/jpeg', 'application/pdf']
    if file_mime_type not in accept:
        print("file type is not supported")
        raise ValidationError("Unsupported file type. Allowed types are: PNG, JPEG, and PDF.")

def validate_file_size(file):
    max_size_mb = 2  # 2MB max file size
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
    
    if file.size > max_size:
        print("file size exceeded")
        raise ValidationError(f"File size should not exceed {max_size_mb} MB.")

def vendor_license_path(instance, filename):
    return f'vendor/license/{instance.vendor_name}/{filename}'


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.FileField(upload_to=vendor_license_path, validators=[validate_file_mimetype, validate_file_size])
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    modified_at = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):
        if not self.vendor_slug:
            base_slug = slugify(self.vendor_name)
            slug = base_slug
            num = 1
            while Vendor.objects.filter(vendor_slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.vendor_slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.vendor_name
