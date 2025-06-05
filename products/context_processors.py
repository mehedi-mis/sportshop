from .models import Category
from django.shortcuts import redirect


def get_menu_categories(request):
    categories = Category.objects.filter(is_active=True)
    context = {
        'menu_categories': categories,
    }
    return context
