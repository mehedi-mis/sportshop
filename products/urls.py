from django.urls import path
from .views import (
    ProductListView, ProductDetailView,
    ProductCreateView, ProductUpdateView, ProductDeleteView,
    CategoryListView, CategoryDetailView,
    CategoryCreateView, CategoryUpdateView, CategoryDeleteView
)


urlpatterns = [
    # # Admin Product URLs
    path('product/add/', ProductCreateView.as_view(), name='product_create'),
    path('product/<slug:slug>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('product/<slug:slug>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('category/<slug:category_slug>/', ProductListView.as_view(), name='product_list_by_category'),

    # Admin Category URLs
    path('categories/<slug:slug>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<slug:slug>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    # Product URLs
    path('', ProductListView.as_view(), name='product_list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]
