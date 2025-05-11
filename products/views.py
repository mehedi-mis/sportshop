from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .models import Category, Product, ProductImage
from .forms import ProductForm, ProductImageFormSet, CategoryForm


class ProductListView(ListView):
    """# Product List View"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)

        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            descendants = category.get_descendants(include_self=True)
            queryset = queryset.filter(category__in=descendants)

        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )

        # Sorting
        sort_by = self.request.GET.get('sort_by', 'created_at')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['current_category'] = self.kwargs.get('category_slug')
        return context


class ProductDetailView(DetailView):
    """# Product Detail View"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(pk=self.object.pk)[:4]
        # Add breadcrumbs
        context['breadcrumbs'] = [
            {'name': 'Products', 'url': reverse('product_list')},
            {'name': product.category.name, 'url': product.category.get_absolute_url()},
            {'name': product.name, 'url': product.get_absolute_url()}
        ]
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['current_category'] = product.category.slug
        return context


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Admin Product Create View"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProductImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = ProductImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Product created successfully!')
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Admin Product Update View"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProductImageFormSet(
                self.request.POST, self.request.FILES,
                instance=self.object
            )
        else:
            context['formset'] = ProductImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Product updated successfully!')
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """# Admin Product Delete View"""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')
    success_message = "Product was deleted successfully"

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class CategoryListView(ListView):
    """Category Views"""
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True, is_active=True)


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        context['products'] = Product.objects.filter(
            category=category,
            is_active=True
        )[:12]
        context['breadcrumbs'] = self.get_breadcrumbs(category)
        context['subcategories'] = self.object.get_children().filter(is_active=True)
        return context

    def get_breadcrumbs(self, category):
        return [{
            'name': ancestor.name,
            'url': ancestor.get_absolute_url()
        } for ancestor in category.get_ancestors(include_self=True)]


class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Admin Category Views"""
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return self.request.user.is_staff


class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return self.request.user.is_staff


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'products/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        if self.object.get_children().exists() or self.object.products.exists():
            messages.error(
                self.request,
                "You cannot delete this category because it has subcategories or products"
            )
            return redirect('category_list')
        return super().form_valid(form)
