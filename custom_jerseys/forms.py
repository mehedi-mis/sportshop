from django import forms
from .models import CustomJerseyOrder
from products.models import Product


class CustomJerseyOrderForm(forms.ModelForm):
    class Meta:
        model = CustomJerseyOrder
        fields = [
            'name_on_jersey', 'jersey_number', 'size',
            'primary_color', 'secondary_color', 'team_logo',
            'design_preferences', 'reference_image'
        ]
        widgets = {
            'design_preferences': forms.Textarea(attrs={'rows': 4}),
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['size'].choices = Product.SIZE_CHOICES
        self.fields['secondary_color'].required = False

class CustomJerseyStatusForm(forms.ModelForm):
    class Meta:
        model = CustomJerseyOrder
        fields = ['status', 'price']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }