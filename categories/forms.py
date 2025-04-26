from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'color', 'icon']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'placeholder': 'Enter an emoji or icon name', 'class': 'form-control'}),
        }
        labels = {
            'icon': 'Icon (emoji or name)',
        }
        help_texts = {
            'icon': 'You can use emoji (e.g., 🍎) or an icon name',
        }