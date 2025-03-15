from django import template


register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get the value from a dictionary for a given key"""
    return dictionary.get(key, [])


@register.filter
def key_exists(dict_obj, key):
    return key in dict_obj if dict_obj else False