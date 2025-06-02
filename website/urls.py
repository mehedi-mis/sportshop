from django.urls import path
from website.views import (
home_page, SiteConfigListView, SiteConfigCreateView, SiteConfigUpdateView, SiteConfigDeleteView,
BannerListView, BannerCreateView, BannerUpdateView, BannerDeleteView, BannerDetailView
)


urlpatterns = [
    path('', home_page, name='home'),

    # Site Config
    path('site-config/', SiteConfigListView.as_view(), name='site_config_list'),
    path('site-config/add/', SiteConfigCreateView.as_view(), name='site_config_create'),
    path('site-config/<int:pk>/edit/', SiteConfigUpdateView.as_view(), name='site_config_edit'),
    path('site-config/<int:pk>/delete/', SiteConfigDeleteView.as_view(), name='site_config_delete'),

    # Banner
    path('banners/', BannerListView.as_view(), name='banner_list'),
    path('banners/add/', BannerCreateView.as_view(), name='banner_create'),
    path('banners/<int:pk>/edit/', BannerUpdateView.as_view(), name='banner_edit'),
    path('banners/<int:pk>/delete/', BannerDeleteView.as_view(), name='banner_delete'),
    path('banners/<int:pk>/', BannerDetailView.as_view(), name='banner_detail'),
]
