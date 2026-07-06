class NetworkFilterMixin:
    """
    Filters a queryset based on the networks of the current user.
    Depending on the model's direct networks M2M, organization FK
    method FK or campaign FK
    """

    def filter_queryset_by_network(self, request, qs):
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="Governance Admins").exists()
        ):
            return qs

        user_networks = request.user.profile.organization.networks.all()
        if not user_networks:
            return qs.none()

        # Used in: organizations
        if hasattr(qs.model, "networks"):
            return qs.filter(networks__in=user_networks)

        # Used in: surveys
        if hasattr(qs.model, "method"):
            return qs.filter(method__networks__in=user_networks)

        # Used in: indicators
        if hasattr(qs.model, "methods"):
            return qs.filter(methods__networks__in=user_networks)

        # Used in: users
        if hasattr(qs.model, "profile"):
            return qs.filter(profile__organization__networks__in=user_networks)

        return qs.none()

    def filter_model_by_network(self, request, model, **filters):
        qs = model.objects.filter(**filters)
        return self.filter_queryset_by_network(request, qs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return self.filter_queryset_by_network(request, qs)
