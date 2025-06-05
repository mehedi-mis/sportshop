from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Wishlist, WishlistItem
from products.models import Product


class WishlistView(LoginRequiredMixin, ListView):
    model = WishlistItem
    template_name = 'wishlist/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist.items.select_related('product').all()


def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to add items to your wishlist")
        return redirect('login')

    product = get_object_or_404(Product, pk=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
        messages.info(request, "This product is already in your wishlist")
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        messages.success(request, f"{product.name} added to your wishlist")

    return redirect(request.META.get('HTTP_REFERER', 'product_detail'))


def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id, wishlist__user=request.user)
    product_name = item.product.name
    item.delete()
    messages.success(request, f"{product_name} removed from your wishlist")
    return redirect('wishlist')