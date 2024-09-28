from .models import User
from django import forms
import re


class UserForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "first_name",
                "placeholder": "Enter your first name",
            }
        )
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "last_name",
                "placeholder": "Enter your last name",
            }
        )
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "username",
                "placeholder": "Enter your username"
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "email",
                "placeholder": "Enter your email"
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "password"
            }
        ),
        min_length=8
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "confirm_password",
            }
        )
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password'
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Passwords does not match"
            )
        
        if not re.search(r'\d', password):
            raise forms.ValidationError(
                "The password must contain at least one digit (0-9)."
            )
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError(
                "The password must contain at least one uppercase letter (A-Z)."
            )
    
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError(
                "The password must contain at least one lowercase letter (a-z)."
            )
        
        if not re.search(r'[\W_]', password):
            raise forms.ValidationError(
                "The password must contain at least one special character (!@#$%^&*)."
            )
