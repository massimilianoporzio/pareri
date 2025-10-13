from django import template

register = template.Library()


@register.filter
def length_is(value, arg):
    """Returns True if the value's length is equal to arg."""
    try:
        return len(value) == int(arg)
    except Exception:
        return False
