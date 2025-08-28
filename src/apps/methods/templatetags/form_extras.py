from django.template import Library

register = Library()


@register.filter
def get_item(form, field_name):
    return form[field_name]
