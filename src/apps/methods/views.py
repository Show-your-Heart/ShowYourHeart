import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin

from apps.geodata.models import Region3
from apps.methods.forms import get_form_sections
from apps.methods.mixins import MethodFillMixin

from .helpers import (
    ParseExternalInvitations,
    get_external_survey_filter,
    get_survey_stats,
)
from .models import Campaign, Invitation, Method, Survey
from .services import send_invitation


class MethodFillView(MethodFillMixin, TemplateView):
    template_name = "methods/method_fill.html"

    def get_context_data(self, **kwargs):
        method = Method.objects.get(pk=self.kwargs["id"])
        kwargs["campaign"] = Campaign.objects.get(
            methods__id__contains=method.id, status=True
        ).id
        kwargs["method"] = method
        return super().get_context_data(**kwargs)

    def post(self, request, id):
        method_id = id
        try:
            campaign = Campaign.objects.get(
                methods__id__contains=method_id, status=True
            )
        except ObjectDoesNotExist as error:
            raise ObjectDoesNotExist(
                _("The method has no asociated campaign and can't be answered")
            ) from error

        return super().post(request, method_id, campaign.id)


@method_decorator(login_not_required, name="dispatch")
class ExternalMethodFillView(MethodFillMixin, TemplateView):
    template_name = "methods/method_fill.html"

    def get_context_data(self, **kwargs):
        invitation = Invitation.objects.get(token=self.kwargs["id"])

        kwargs["campaign"] = invitation.external_survey_invitation.campaign.id
        kwargs["method"] = invitation.external_survey_invitation.external_survey
        return super().get_context_data(**kwargs)

    def post(self, request, id):
        action = request.POST.get("action")
        invitation = Invitation.objects.get(token=id)
        if action == "submit":
            invitation.status = Invitation.Status.FILLED
            invitation.save()

        return super().post(
            request,
            invitation.external_survey_invitation.external_survey.id,
            invitation.external_survey_invitation.campaign.id,
        )


def invitations_sent_view(request, id):
    invitations = Invitation.objects.filter(
        external_survey_invitation_id=id, status=Invitation.Status.PENDING
    )
    if invitations:
        for invitation in invitations:
            send_invitation(invitation)
            invitation.status = Invitation.Status.SENT
            invitation.save()

        messages.success(
            request,
            _("The invitations have been sent."),
        )
    else:
        messages.success(
            request,
            _("There are no invitations to send."),
        )

    return redirect(request.META.get("HTTP_REFERER", "/"))


def invitation_sent_view(request, id):
    invitation = Invitation.objects.get(pk=id)
    send_invitation(invitation)
    invitation.status = Invitation.Status.SENT
    invitation.save()

    messages.success(
        request,
        _("The invitation has been sent."),
    )

    return redirect(request.META.get("HTTP_REFERER", "/"))


def import_csv(request, id):
    if request.method == "POST":
        csv_file = request.FILES["csv_file"]
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.reader(decoded_file)
        pei = ParseExternalInvitations()
        message = pei.parse_csv(reader, id)

        if len(message) > 0:
            messages.warning(
                request,
                "\n".join(message),
            )
        return HttpResponseRedirect(request.path_info)
    messages.success(
        request,
        _("The CSV has been imported correctly."),
    )
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_http_methods("GET")
def load_ext_surveys(request):
    if network_owner_id := request.GET.get("network_owner"):
        try:
            methods = get_external_survey_filter(network_owner_id)
        except Method.DoesNotExist:
            pass
    else:
        methods = []
    return render(request, "organizations/methods_options.html", {"methods": methods})


class BalanceReview(UnfoldModelAdminViewMixin, TemplateView):
    title = "Balance review"
    permission_required = ()
    template_name = "admin/methods/balance_review.html"

    def post(self, request, *args, **kwargs):
        # Save the form values on the view instance so ``get_context_data`` can use it
        self.filtered_campaign_id = request.POST.get("campaign")
        self.filtered_region3_id = request.POST.get("region3")
        self.filtered_method_id = request.POST.get("method")
        self.filtered_status_id = request.POST.get("status")
        self.filtered_unit_of_analysis = request.POST.get("unit-analysis")

        return self.get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        campaign_id = getattr(self, "filtered_campaign_id", None)
        region3_id = getattr(self, "filtered_region3_id", None)
        method_id = getattr(self, "filtered_method_id", None)
        status_id = getattr(self, "filtered_status_id", None)
        unit_of_analysis_id = getattr(self, "filtered_unit_of_analysis", None)

        print(campaign_id)
        print(region3_id)
        print(method_id)
        print(status_id)
        print(unit_of_analysis_id)

        nif_filter = self.request.GET.get("nif") or ""
        name_filter = self.request.GET.get("name") or ""
        print(self.request.GET)
        print(nif_filter)
        print(name_filter)
        all_surveys = Survey.objects.filter(
            organization__vat_number__icontains=nif_filter,
            organization__name__icontains=name_filter,
            organization__region3_id=region3_id,
            campaign_id=campaign_id,
            method_id=method_id,
            status=status_id,
            method__unit_of_analysis=unit_of_analysis_id,
        )

        context["nif_filter"] = nif_filter
        context["name_filter"] = name_filter

        for s in all_surveys:
            s.status = Survey.Status(s.status).label

            method = {
                "id": s.method.id,
                "name": s.method.name,
                "sections": get_form_sections(s.method),
            }

            stats = get_survey_stats(s, method)
            s.totalProgress = stats["totalProgress"]

        all_status = []
        for s in Survey.Status:
            all_status.append({"id": s.value, "name": s.label})
        unit_of_analysis = []
        for ua in Method.UnitAnalysis:
            unit_of_analysis.append({"id": ua.value, "name": ua.label})

        context["surveys"] = all_surveys
        context["campaigns"] = Campaign.objects.all()
        context["regions"] = Region3.objects.all()
        context["methods"] = Method.objects.all()
        context["unitanalysis"] = unit_of_analysis
        context["status"] = all_status

        return context
