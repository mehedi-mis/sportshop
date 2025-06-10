from decimal import Decimal, InvalidOperation
from products.models import Product

from django.conf import settings
from .models import Cart, CartItem


class SessionCart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.discount_price)
            }
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
            
        for item in cart.values():
            try:
                # Ensure price is properly converted to Decimal
                price_str = str(item['price']).strip()  # Convert to string and remove whitespace
                # Remove any non-numeric characters except decimal point and minus
                cleaned_price = ''.join(c for c in price_str if c.isdigit() or c in '.-')
                item['price'] = Decimal(cleaned_price)
                item['total_price'] = item['price'] * item['quantity']
                yield item
            except (InvalidOperation, TypeError, ValueError) as e:
                # Handle the error appropriately - log it and set a default value or skip
                print(f"Error converting price for item: {item}. Error: {e}")
                # Option 1: Set a default price (e.g., 0) and continue
                item['price'] = Decimal('0')
                item['total_price'] = Decimal('0')
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
