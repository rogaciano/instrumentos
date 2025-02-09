from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtrai o argumento do valor"""
    try:
        return float(value or 0) - float(arg or 0)
    except (ValueError, TypeError):
        return 0
