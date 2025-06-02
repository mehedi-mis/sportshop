from django.shortcuts import render
from .models import SiteConfiguration, Banner
from products.models import Product

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import SiteConfigurationForm, BannerForm


def home_page(request):
    site_config = SiteConfiguration.objects.first()  # Assuming single config instance
    banners = Banner.objects.filter(is_active=True).order_by('-created_at')[:5]
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]  # latest 8 products

    context = {
        'site_config': site_config,
        'banners': banners,
        'products': products,
    }
    return render(request, 'home.html', context)


# Site Configuration CRUD
class SiteConfigListView(ListView):
    model = SiteConfiguration
    template_name = 'site_config/list.html'
    context_object_name = 'configs'


class SiteConfigCreateView(CreateView):
    model = SiteConfiguration
    form_class = SiteConfigurationForm
    template_name = 'site_config/form.html'
    success_url = reverse_lazy('site_config_list')


class SiteConfigUpdateView(UpdateView):
    model = SiteConfiguration
    form_class = SiteConfigurationForm
    template_name = 'site_config/form.html'
    success_url = reverse_lazy('site_config_list')


class SiteConfigDeleteView(DeleteView):
    model = SiteConfiguration
    template_name = 'site_config/confirm_delete.html'
    success_url = reverse_lazy('site_config_list')


# Banner CRUD
class BannerListView(ListView):
    model = Banner
    template_name = 'banner/list.html'
    context_object_name = 'banners'


class BannerCreateView(CreateView):
    model = Banner
    form_class = BannerForm
    template_name = 'banner/form.html'
    success_url = reverse_lazy('banner_list')


class BannerUpdateView(UpdateView):
    model = Banner
    form_class = BannerForm
    template_name = 'banner/form.html'
    success_url = reverse_lazy('banner_list')


class BannerDeleteView(DeleteView):
    model = Banner
    template_name = 'banner/confirm_delete.html'
    success_url = reverse_lazy('banner_list')


class BannerDetailView(DetailView):
    model = Banner
    template_name = 'banner/detail.html'
    context_object_name = 'banner'

