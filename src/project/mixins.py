from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class AnonymousRequiredMixin(AccessMixin):
    """Verify that the current user is not authenticated."""

    # For the django-login-required-mixin
    login_required = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        url = settings.LOGIN_REDIRECT_URL if settings.LOGIN_REDIRECT_URL else ""
        return redirect(url)


class NetworkFilterMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(
            name="Governance Admins"
        ):
            return qs
        if hasattr(request.user, "network") and request.user.network:
            return qs.filter(networks=request.user.network)
        return qs.none()
