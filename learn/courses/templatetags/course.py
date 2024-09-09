from django import template
from django.utils.safestring import mark_safe
import markdown
from django.contrib.auth.models import Group
from courses.models import OverallPerformance


register = template.Library()


@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None


@register.filter(name="markdown")
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.filter(name="has_group")
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


from django import template


@register.filter
def get_item(dictionary, key):
    """Returns the value for the key in a dictionary."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
