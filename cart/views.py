from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .utils import SessionCart
from django.views.decorators.http import require_POST


@require_POST
def cart_add(request, product_id):
    cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    update_quantity = request.POST.get('update', False) == 'true'

    cart.add(
        product=product,
        quantity=quantity,
        update_quantity=update_quantity
    )
    return redirect('cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def cart_detail(request):
    cart = SessionCart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


def cart_clear(request):
    cart = SessionCart(request)
    cart.clear()
    return redirect('cart_detail')