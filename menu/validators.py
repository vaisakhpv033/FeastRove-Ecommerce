from django.core.exceptions import ValidationError


def validate_positive_price(value):
    if value <= 0:
        raise ValidationError("Price must be greater than zero.")
