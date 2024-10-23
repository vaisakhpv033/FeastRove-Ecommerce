from vendor.models import Vendor
from feastrove.settings import PAYPAL_CLIENT_ID, GOOGLE_API_KEY

def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None
    return {
        "vendor": vendor,
    }


def get_paypal_client_id(request):
    return {'PAYPAL_CLIENT_ID': PAYPAL_CLIENT_ID}


def get_google_api_key(request):
    return {'google_api_key': GOOGLE_API_KEY}