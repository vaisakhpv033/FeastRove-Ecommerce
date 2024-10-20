import re

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
# from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.models import Site

def detect_user(user):
    if user.role == 1:
        redirect_url = "vendorDashboard"
    elif user.role == 2:
        redirect_url = "customerDashboard"
    elif user.role is None and user.is_superadmin:
        redirect_url = "adminDashboard"
    return redirect_url


# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

# to send verification email
def send_verification_email(user, *, email_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = Site.objects.get_current()
    message = render_to_string(
        email_template,
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    to_email = user.email
    mail = EmailMessage(email_subject, message, from_email, to=[to_email])
    mail.send()


# to send notification email regarding approval
def send_notification(email_subject, email_template, context, to_email=None):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template, context)
    if not to_email:
        to_email = [context['user'].email]
    mail = EmailMessage(email_subject, message, from_email, to=to_email)
    mail.send()
    

def validate_password(password):
    if not (
        re.search(r"\d", password)
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"[\W_]", password)
    ):
        raise ValidationError(
            "The password must contain at least one digit, one uppercase letter, one lowercase letter, and one special character."
        )
    elif len(password )< 8:
        raise ValidationError(
        "The minimum length of password is 8"
        )