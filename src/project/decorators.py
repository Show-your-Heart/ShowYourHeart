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
