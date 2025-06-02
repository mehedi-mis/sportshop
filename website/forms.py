# forms.py
from django import forms
from .models import SiteConfiguration, Banner


class SiteConfigurationForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = '__all__'


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = '__all__'
