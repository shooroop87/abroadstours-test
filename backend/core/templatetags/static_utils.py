# core/templatetags/static_utils.py
from django import template
from django.conf import settings
from django.contrib.staticfiles import finders

register = template.Library()


@register.simple_tag
def safe_static(path, fallback="img/image_not_found.png"):
    if finders.find(path):
        return f"{settings.STATIC_URL}{path}"
    return f"{settings.STATIC_URL}{fallback}"
