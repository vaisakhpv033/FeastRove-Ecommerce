from django import forms 
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["category_name", "description", "parent"]


    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.filter(parent__isnull=True)
        self.fields['parent'].required = True