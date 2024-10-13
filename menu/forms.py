from django import forms

from .models import Category, FoodItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["category_name", "description", "parent"]

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields["parent"].queryset = Category.objects.filter(parent__isnull=True)
        self.fields["parent"].required = True


class FoodItemForm(forms.ModelForm):
    image = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "class": "btn btn-info w-100",
            }
        ),
    )

    class Meta:
        model = FoodItem
        fields = [
            "category",
            "food_title",
            "description",
            "price",
            "image",
            "is_available",
        ]

    def __init__(self, *args, **kwargs):
        vendor = kwargs.pop("vendor", None)
        super().__init__(*args, **kwargs)
        if vendor:
            self.fields["category"].queryset = Category.objects.filter(vendor=vendor)
        else:
            self.fields["category"].queryset = Category.objects.none()
