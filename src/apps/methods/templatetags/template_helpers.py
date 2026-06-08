from urllib.parse import urlencode

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


@register.filter
def toggle_sort(query_dict, param):
    # Make a copy because QueryDict instance is immutable
    params = query_dict.copy()
    current_value = query_dict.get("o", "")

    if current_value == param:
        params["o"] = "-" + param
    elif current_value == "-" + param:
        params["o"] = param
    else:
        params["o"] = param

    return urlencode(params, doseq=True)
