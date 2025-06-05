from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def add_shipping_cost(cart, shipping_cost):
    return cart.get_total_price() + Decimal(str(shipping_cost))
