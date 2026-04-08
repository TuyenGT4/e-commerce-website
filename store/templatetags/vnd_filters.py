from django import template

register = template.Library()

@register.filter
def vnd(value):
    """Định dạng số tiền theo VND: 23.000.000đ"""
    try:
        value = int(value)
        return f"{value:,}đ".replace(",", ".")
    except (ValueError, TypeError):
        return "0đ"