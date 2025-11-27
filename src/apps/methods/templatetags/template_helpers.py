from django.template import Library

register = Library()


@register.filter
def get_id(path):
    search_string = "methods/method/"
    start_id_index = path.index(search_string) + len(search_string)
    end_id_index = start_id_index + 36  # The GUID length is 36
    return path[start_id_index:end_id_index]


@register.filter
def stripe_whitespaces(text):
    return text.replace(" ", "")
