from django import template

register = template.Library()

@register.filter
def percentage(value, total):
    """Calculate percentage of value from total"""
    try:
        return float(value) / float(total) * 100
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def add(value, arg):
    return value + arg
