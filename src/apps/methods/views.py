import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, TemplateView
from unfold.views import UnfoldModelAdminViewMixin

from apps.geodata.models import Region3
from apps.methods.mixins import MethodFillMixin

from .helpers import (
    ParseExternalInvitations,
    get_external_survey_filter,
    get_form_sections,
    get_survey_stats,
)
from .models import Campaign, Invitation, Method, Survey
from .services import send_invitation


class MethodFillView(MethodFillMixin, TemplateView):
    template_name = "methods/method_fill.html"

    def get_context_data(self, **kwargs):
        method = Method.objects.get(pk=self.kwargs["id"])
        if "campaign_id" in self.kwargs:
            self.kwargs["campaign"] = self.kwargs["campaign_id"]

        kwargs["method"] = method
        return super().get_context_data(**kwargs)

    def post(self, request, id, **kwargs):
        method_id = id
        project_id = self.kwargs.get("project_id")

        return super().post(
            request, method_id, self.kwargs.get("campaign_id"), project_id
        )


@method_decorator(login_not_required, name="dispatch")
class ExternalMethodFillView(MethodFillMixin, TemplateView):
    template_name = "methods/method_fill.html"

    def get_context_data(self, **kwargs):
        invitation = Invitation.objects.get(token=self.kwargs["id"])

        kwargs["campaign_id"] = invitation.external_survey_invitation.campaign.id
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


class BalanceReviewView(UnfoldModelAdminViewMixin, ListView):
    title = "Balance review"
    permission_required = ()
    template_name = "admin/methods/survey_review.html"
    paginate_by = 20

    def get_queryset(self):
        all_surveys = Survey.objects.filter(
            self.get_survey_query(self.request.GET)
        ).order_by("-start_date")

        return all_surveys

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        page = context["page_obj"]
        processed = []
        for s in page.object_list:
            s.status = Survey.Status(s.status).value
            s.method.sections = get_form_sections(s.method)

            stats = get_survey_stats(s, s.method, s.campaign)
            s.totalProgress = stats["totalProgress"]
            processed.append(s)

        all_status = []
        for s in Survey.Status:
            all_status.append({"id": s.value, "name": s.label})
        unit_of_analysis = []
        for ua in Method.UnitAnalysis:
            unit_of_analysis.append({"id": ua.value, "name": ua.label})

        campaigs = Campaign.objects.all()
        for c in campaigs:
            c.name = f"{c.name} | {c.year}"

        context["campaigns"] = campaigs
        context["regions"] = Region3.objects.all()
        context["methods"] = Method.objects.all()
        context["unitanalysis"] = unit_of_analysis
        context["status"] = all_status

        # Set variables to display them back on the survey_review.html
        context["nif_filter"] = self.request.GET.get("nif") or ""
        context["name_filter"] = self.request.GET.get("name") or ""
        context["campaign_filter"] = self.request.GET.get("campaign") or ""
        context["region3_filter"] = self.request.GET.get("region3") or ""
        context["method_filter"] = self.request.GET.get("method") or ""
        context["status_filter"] = self.request.GET.get("status") or ""
        context["unit_analysis_filter"] = self.request.GET.get("unit-analysis") or ""

        context["object_list"] = processed

        return context

    def get_survey_query(self, get_request):
        nif_filter = get_request.get("nif") or ""
        name_filter = get_request.get("name") or ""
        campaign_filter = get_request.get("campaign") or ""
        region3_filter = get_request.get("region3") or ""
        method_filter = get_request.get("method") or ""
        status_filter = get_request.get("status") or ""
        unit_analysis_filter = get_request.get("unit-analysis") or ""

        query = Q(
            organization__vat_number__icontains=nif_filter,
            organization__name__icontains=name_filter,
        )
        if region3_filter:
            query &= Q(organization__region3_id=region3_filter)
        if campaign_filter:
            query &= Q(campaign_id=campaign_filter)
        if method_filter:
            query &= Q(method_id=method_filter)
        if status_filter:
            query &= Q(status=status_filter)
        if unit_analysis_filter:
            query &= Q(method__unit_of_analysis=unit_analysis_filter)

        return query
