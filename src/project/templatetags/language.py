from django.template import Library
from django.urls import Resolver404, resolve, reverse
from django.utils.translation import activate, get_language

register = Library()


@register.simple_tag(takes_context=True)
def change_lang(context, lang=None, *args, **kwargs):
    """
    Get active page's url by a specified language
    Usage: {% change_lang 'en' %}
    """

    # When generating the language change url, it won't be able to generate it
    # for a non-existent URL.
    # For instance, if you access http://localhost:1234/asdasdadsad, the 404
    # template shown contains the language selection menu, therefore, will be
    # trying to generate the localized version of this URL.
    # In these kind of situations, it can happen that request is not in
    # context, and also that resolve() raises a Resolver404.
    # For this reason, we set a fallback default URL, and return it if
    # anything fails.
    default_url = "home"
    request = context.get("request", None)
    if not request:
        return reverse(default_url)

    path = request.path
    try:
        url_parts = resolve(path)
    except Resolver404:
        return reverse(default_url)

    url = path
    cur_language = get_language()
    try:
        activate(lang)
        url = reverse(url_parts.view_name, kwargs=url_parts.kwargs)
    finally:
        activate(cur_language)

    return "%s" % url
