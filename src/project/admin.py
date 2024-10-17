from django.contrib.admin import ModelAdmin as BaseModelAdmin


class ModelAdminMixin(object):
    base_readonly_fields = ("created_at", "created_by", "updated_at")
    # superuser_fields will be read-only unless you are superuser
    superuser_fields = ()

    def get_superuser_fields(self):
        return self.superuser_fields

    def get_base_readonly_fields(self):
        return self.base_readonly_fields

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        fields = tuple(set(fields + self.get_base_readonly_fields()))
        if not request.user.is_superuser:
            return tuple(set(fields + self.get_superuser_fields()))
        return fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        This method ensures that any Inline that is included will fill
        the field `created_by` automatically.

        The interesting fields to play with are:
        for form in formset:
            print("Instance str representation:", form.instance)
            print("Instance dict:", form.instance.__dict__)
            print("Initial for ID field:", form["id"].initial)
            print("Has changed:", form.has_changed())

        form["id"].initial will be None if it's a new entry.
        """
        for form in formset:
            model = type(form.instance)
            if not form["id"].initial and hasattr(model, "created_by"):
                # created_by will not appear in the form dictionary because
                # is read_only, but we can anyway set it directly at the yet-
                # to-be-saved instance.
                form.instance.created_by = request.user
        super().save_formset(request, form, formset, change)


class ModelAdmin(ModelAdminMixin, BaseModelAdmin):
    pass
