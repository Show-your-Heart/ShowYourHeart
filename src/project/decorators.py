from functools import wraps

from django.conf import settings
from django.shortcuts import redirect


def anonymous_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            url = settings.LOGIN_REDIRECT_URL if settings.LOGIN_REDIRECT_URL else ""
            return redirect(url)
        return view_func(request, *args, *kwargs)

    return _wrapped_view


def register_with_default_templates(admin_site, model=None):
    """
    Decorator that registers a model with a given AdminSite using the decorated ModelAd-
    min class, injecting default templates. Can be stacked.
    """

    def decorator(admin_class):
        class WrappedAdmin(admin_class):
            change_form_template = None
            change_list_template = None
            pass

        if model is None:
            raise ValueError("You must pass a model to register_admin.")

        admin_site.register(model, WrappedAdmin)
        return admin_class  # return original class so stacking works

    return decorator


def gov_admin_register(gov_admin_site, model=None):
    """
    Decorator that registers a model with the custom GovAdminSite using the decorated
    ModelAdmin class, injecting custom templates. Can be stacked.
    """

    def decorator(admin_class):
        class WrappedAdmin(admin_class):
            change_form_template = "admin/syh_change_form.html"
            change_list_template = "admin/syh_change_list.html"
            pass

        if model is None:
            raise ValueError("You must pass a model to register_gov_admin.")

        gov_admin_site.register(model, WrappedAdmin)
        return admin_class  # return original class so stacking works

    return decorator
