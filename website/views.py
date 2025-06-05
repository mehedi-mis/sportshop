from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from .models import SiteConfiguration, Banner, ContactUs
from products.models import Product, Category

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import SiteConfigurationForm, BannerForm


def home_page(request):
    try:
        site_config = SiteConfiguration.objects.first()
    except Exception as e:
        site_config = None
    banners = Banner.objects.filter(is_active=True).order_by('-created_at')[:5]
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]  # latest 8 products
    categories = Category.objects.filter(is_active=True)[:3]
    context = {
        'site_config': site_config,
        'banners': banners,
        'products': products,
        'categories': categories,
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


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if name and email and subject and message:
            ContactUs(name=name, email=email,
                      subject=subject, message=message).save()
            try:
                from_email = settings.DEFAULT_FROM_EMAIL
                send_mail(subject, message, from_email, [
                          email],  fail_silently=False,)
                messages.success(request, f"Hello {name},\nThanks for contact with us!")
                return redirect('home')
            except BadHeaderError as error:
                messages.error(request, f"{error}")
                return redirect('home')
        else:
            messages.error(request, f"Mail Subject or message body or your email error")
            return redirect('home')
    else:
        context = {}
        try:
            site_config_obj = SiteConfiguration.objects.first()
        except Exception as e:
            site_config_obj = None

        if site_config_obj:
            context['site_config'] = site_config_obj
        return render(request, 'website/contact.html', context)
