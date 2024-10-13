from django.db import models
from django.utils.text import slugify

from accounts.models import User, UserProfile
from accounts.utils import send_notification
from accounts.validators import validate_file_mimetype, validate_file_size


def vendor_license_path(instance, filename):
    return f"vendor/license/{instance.vendor_name}/{filename}"


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name="userprofile", on_delete=models.CASCADE
    )
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.FileField(
        upload_to=vendor_license_path,
        validators=[validate_file_mimetype, validate_file_size],
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # update
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = "accounts/emails/admin_approval_email.html"
                context = {
                    "user": self.user,
                    "is_approved": self.is_approved,
                }
                if self.is_approved:
                    # send notification email
                    mail_subject = "Congratulations Your restaurant has been approved"
                    send_notification(mail_subject, mail_template, context)
                else:
                    mail_subject = "We're Sorry! You are not eligible for publishing your food menu on our  marketplace"
                    send_notification(mail_subject, mail_template, context)

        if not self.vendor_slug:
            base_slug = slugify(self.vendor_name)
            slug = base_slug
            num = 1
            while Vendor.objects.filter(vendor_slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.vendor_slug = slug
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.vendor_name
