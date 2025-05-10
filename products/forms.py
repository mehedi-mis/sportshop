from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductImage, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'sku', 'price', 'discount_price',
            'stock', 'description', 'size', 'color', 'brand',
            'is_featured', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        discount_price = cleaned_data.get('discount_price')
        price = cleaned_data.get('price')

        if discount_price and discount_price >= price:
            raise forms.ValidationError(
                "Discount price must be lower than regular price"
            )
        return cleaned_data


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=('image', 'is_default'),
    extra=3,
    max_num=5,
    can_delete=True
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent', 'description', 'image', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.exclude(
            pk=self.instance.pk
        ) if self.instance else Category.objects.all()
