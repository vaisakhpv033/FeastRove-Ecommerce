from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import send_verification_email

from .models import User, UserProfile
from wallets.models import Wallet

def handle_role_based_email(instance):
    print("first", instance, instance.role)
    if instance.role in [User.CUSTOMER, User.VENDOR]:
        print("second", instance.role)
        mail_subject = "Activate your account"
        email_template = "accounts/emails/account_verification_email.html"
        send_verification_email(instance, email_subject=mail_subject, email_template=email_template)


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print("user profile is created")
        handle_role_based_email(instance)
        # assigning role's and is active status if signup using google authentication
        if instance.role is None:
            instance.role = User.CUSTOMER
            instance.is_active = True
            instance.save(update_fields=["role", "is_active"])
            # create the wallet for the user
            Wallet.objects.create(user=instance)

    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            UserProfile.objects.create(user=instance)


