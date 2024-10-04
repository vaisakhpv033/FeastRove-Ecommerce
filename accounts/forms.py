import re

from django import forms

from .validators import validate_file_mimetype
from .models import User, UserProfile


class UserForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "first_name",
                "placeholder": "first name",
            }
        ),
        error_messages={
            'required': "First Name is required",
        }
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "last_name",
                "placeholder": "last name",
            }
        ),
        error_messages={
            'required': "Last Name is required",
        }
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "username",
                "placeholder": "username",
            }
        ),
        error_messages={
            'required': "Username is required",
        }
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "email",
                "placeholder": "email",
            }
        ),
        error_messages={
            'required': "Email is required"
        }
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control form-control-lg", "id": "password"}
        ),
        min_length=8,
        error_messages={
            'required': "Password is required",
            'min_length': "Minimum length of password is 8"
        }
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "confirm_password",
            }
        ),
        error_messages={
            'required': "Confirm password is required"
        }
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords does not match")

        if not re.search(r"\d", password):
            raise forms.ValidationError(
                "The password must contain at least one digit (0-9)."
            )

        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError(
                "The password must contain at least one uppercase letter (A-Z)."
            )

        if not re.search(r"[a-z]", password):
            raise forms.ValidationError(
                "The password must contain at least one lowercase letter (a-z)."
            )

        if not re.search(r"[\W_]", password):
            raise forms.ValidationError(
                "The password must contain at least one special character (!@#$%^&*)."
            )
        
    def save(self, role, commit=True):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.create_user(
            first_name = first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
            role = role
        )
        return user
        


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'class': 'btn btn-info w-75',
            }
        ), 
        validators=[validate_file_mimetype],
    )
    cover_photho = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'class': 'btn btn-info w-75',
            }
        ), 
        validators=[validate_file_mimetype],
    )
    class Meta:
        model = UserProfile
        fields = ["profile_picture", "cover_photho", "address", "state", "city", "pin_code", "latitude", "longitude" ]

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field == "latitude" or field == "longitude":
                self.fields[field].widget.attrs['readonly'] = 'readonly'

