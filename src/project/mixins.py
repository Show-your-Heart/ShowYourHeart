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
    def filter_queryset_by_network(self, request, qs):
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="Governance Admins").exists()
        ):
            return qs

        user_network = getattr(request.user, "network", None)
        if not user_network:
            return qs.none()

        # Model has direct 'networks' ManyToManyField
        if hasattr(qs.model, "networks"):
            return qs.filter(networks=user_network)

        # Model has related organization and organization_field defined
        if self.organization_field:
            return qs.filter(**{f"{self.organization_field}__networks": user_network})

        # Model has related method and method_field defined
        if self.organization_field:
            return qs.filter(**{f"{self.method_field}__networks": user_network})

        return qs.none()

    def filter_model_by_network(self, request, model, **filters):
        qs = model.objects.filter(**filters)
        return self.filter_queryset_by_network(request, qs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return self.filter_queryset_by_network(request, qs)
