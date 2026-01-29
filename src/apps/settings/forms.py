from django import forms

from apps.organizations.models import Organization


class NetworkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assigned_organizations = Organization.objects.filter(networks__isnull=False)

        if self.instance.pk:
            network_organizations = self.instance.organizations.all()

            self.fields["organizations"].queryset = (
                Organization.objects.exclude(
                    pk__in=assigned_organizations.values_list("pk", flat=True)
                )
                | network_organizations
            )

        else:
            self.fields["organizations"].queryset = Organization.objects.filter(
                networks__isnull=True
            )
