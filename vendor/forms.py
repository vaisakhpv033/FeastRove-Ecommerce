from django import forms 
from .models import Vendor 

class VendorForm(forms.ModelForm):
    vendor_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "vendor_name",
                "placeholder": "Restaurant name",
            }
        )
    )

    vendor_license = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "vendor_license",
            }
        )
    )

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
        