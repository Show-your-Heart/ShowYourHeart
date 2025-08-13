from django.conf import settings


def absolute_url(path):
    return f"{settings.ABSOLUTE_URL}{path}"


def get_model_from_app_list(app_list, app_name, model_name):
    for app in app_list:
        if app["app_label"] == app_name:
            for model in app["models"]:
                if model["object_name"] == model_name:
                    return model


def available_apps_to_dict(available_apps):
    apps_dict = {}
    for app in available_apps:
        models_dict = {}
        for model in app["models"]:
            models_dict[model["object_name"]] = model
        app["models_dict"] = models_dict
        apps_dict[app["name"]] = app

    return apps_dict


def register_with_default_templates(admin_site, model=None, **template_overrides):
    """
    Decorator that registers a model with a given AdminSite using the decorated ModelAdmin class,
    injecting setting templates. Can be stacked.
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
