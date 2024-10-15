from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "full_name",
            "phone_number",
            "pincode",
            "state",
            "city",
            "address",
            "road_name",
            "landmark",
        ]
