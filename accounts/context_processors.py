from typing import Dict, Optional

from django.http import HttpRequest

from feastrove.settings import GOOGLE_API_KEY, PAYPAL_CLIENT_ID
from vendor.models import Vendor


def get_vendor(request: HttpRequest) -> Dict[str, Optional[Vendor]]:
    """
    Retrieve the vendor instance if the logged-in user is a vendor.

    Args:
        request (HttpRequest): The HTTP request object, containing user information.

    Returns:
        dict: A dictionary with a 'vendor' key holding the Vendor instance or None if not found.
    """

    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        vendor = None
    except Exception as e:
        print(e)
        vendor = None
    return {
        "vendor": vendor,
    }


def get_paypal_client_id(request: HttpRequest) -> Dict[str, str]:
    """
    Retrieve the PayPal client ID for the frontend.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary containing the PayPal client ID.
    """
    return {"PAYPAL_CLIENT_ID": PAYPAL_CLIENT_ID}


def get_google_api_key(request: HttpRequest) -> Dict[str, str]:
    """
    Retrieve the Google API key for the frontend.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary containing the Google API key.
    """
    return {"google_api_key": GOOGLE_API_KEY}
