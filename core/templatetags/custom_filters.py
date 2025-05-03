from django import template

register = template.Library()

@register.filter
def percentage(value, arg):
    """Calculate percentage of value relative to arg"""
    try:
        return float(value) / float(arg) * 100
    except (ValueError, ZeroDivisionError, TypeError):  # ← included this
        return 0