from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    coupon_code = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ['payment_method', 'shipping_address', 'billing_address', 'coupon_code']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
            'billing_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['billing_address'].required = False


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
