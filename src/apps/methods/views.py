import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, TemplateView
from unfold.views import UnfoldModelAdminViewMixin

from apps.geodata.models import Region1
from apps.methods.forms import InvitationCreationForm
from apps.methods.mixins import MethodFillMixin
from project.mixins import NetworkFilterMixin

from .helpers import (
    ParseExternalInvitations,
    get_external_survey_filter,
    get_form_sections,
    get_survey_stats,
)
from .models import Campaign, ExternalSurveyInvitation, Invitation, Method, Survey
from .services import send_invitation


class MethodFillView(MethodFillMixin, TemplateView):
    template_name = "methods/method_fill.html"

    def get_context_data(self, **kwargs):
        method = Method.objects.get(pk=self.kwargs["method_id"])
        kwargs["campaign_id"] = self.kwargs["campaign_id"]
        kwargs["method"] = method
        return super().get_context_data(**kwargs)

    def post(self, request, method_id, campaign_id, **kwargs):
        project_id = self.kwargs.get("project_id")
        return super().post(request, method_id, campaign_id, project_id)


class MethodPreviewView(MethodFillMixin, TemplateView):
    template_name = "methods/method_fill.html"

    def get_context_data(self, **kwargs):
        method = Method.objects.get(pk=self.kwargs["method_id"])
        kwargs["method"] = method
        return super().get_context_data(**kwargs)

    def post(self, request, method_id):
        return HttpResponse(status=204)


class ExternalSurveysView(TemplateView):
    template_name = "methods/external_surveys_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        methods = Method.objects.filter(
            unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY
        )

        selected_method_id = self.request.GET.get("method")
        selected_method = (
            methods.filter(id=selected_method_id).first()
            if selected_method_id
            else methods.first()
        )
        invitations = Invitation.objects.none()
        send_invitations_url = None

        if selected_method_id:
            selected_method = methods.filter(id=selected_method_id).first()
        else:
            selected_method = methods.first()

        if selected_method:
            survey_invitations = ExternalSurveyInvitation.objects.filter(
                external_survey=selected_method
            )
            invitations = Invitation.objects.filter(
                external_survey_invitation__in=survey_invitations
            )

            extsurvinv_to_send = survey_invitations.first()
            if extsurvinv_to_send:
                send_invitations_url = reverse(
                    "methods:send_invitations",
                    args=[extsurvinv_to_send.id],
                )

        context.update(
            {
                "methods": methods,
                "selected_method": selected_method,
                "invitations": invitations,
                "create_invitation_form": InvitationCreationForm,
                "send_invitations_url": send_invitations_url,
            }
        )

        return context


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
            invitation.send_date = timezone.now()
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
    invitation.send_date = timezone.now()
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
    if network_id := request.GET.get("network"):
        try:
            methods = get_external_survey_filter(network_id)
        except Method.DoesNotExist:
            pass
    else:
        methods = []
    return render(request, "organizations/methods_options.html", {"methods": methods})


class BalanceReviewView(UnfoldModelAdminViewMixin, ListView, NetworkFilterMixin):
    title = "Balance review"
    permission_required = ()
    template_name = "admin/methods/survey_review.html"
    paginate_by = 20
    organization_field = "organization"
    method_field = "method"

    def get_queryset(self):
        all_surveys = Survey.objects.filter(
            self.get_survey_query(self.request.GET)
        ).order_by("-start_date")

        all_surveys = self.filter_queryset_by_network(self.request, all_surveys)

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

        campaigns = Campaign.objects.all()
        for c in campaigns:
            c.name = f"{c.name} | {c.year}"

        context["campaigns"] = campaigns
        context["regions"] = Region1.objects.all()
        context["methods"] = Method.objects.all()
        context["unitanalysis"] = unit_of_analysis
        context["status"] = all_status

        # Set variables to display them back on the survey_review.html
        context["nif_filter"] = self.request.GET.get("nif") or ""
        context["name_filter"] = self.request.GET.get("name") or ""
        context["campaign_filter"] = self.request.GET.get("campaign") or ""
        context["region1_filter"] = self.request.GET.get("region1") or ""
        context["method_filter"] = self.request.GET.get("method") or ""
        context["status_filter"] = self.request.GET.get("status") or ""
        context["unit_analysis_filter"] = self.request.GET.get("unitanalysis") or ""

        context["object_list"] = processed

        return context

    def get_survey_query(self, get_request):
        nif_filter = get_request.get("nif") or ""
        name_filter = get_request.get("name") or ""
        campaign_filter = get_request.get("campaign") or ""
        region1_filter = get_request.get("region1") or ""
        method_filter = get_request.get("method") or ""
        status_filter = get_request.get("status") or ""
        unit_analysis_filter = get_request.get("unitanalysis") or ""

        query = Q(
            organization__vat_number__icontains=nif_filter,
            organization__name__icontains=name_filter,
        )
        if region1_filter:
            query &= Q(organization__region1_id=region1_filter)
        if campaign_filter:
            query &= Q(campaign_id=campaign_filter)
        if method_filter:
            query &= Q(method_id=method_filter)
        if status_filter:
            query &= Q(status=status_filter)
        if unit_analysis_filter:
            query &= Q(method__unit_of_analysis=unit_analysis_filter)

        return query


@require_http_methods("POST")
def create_invitation_action(request):
    method_id = request.POST.get("method_id")

    if not method_id:
        return HttpResponseBadRequest("Missing method_id")

    selected_method = get_object_or_404(
        Method,
        id=method_id,
        unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY,
    )

    extsurvinv, _ = ExternalSurveyInvitation.objects.get_or_create(
        external_survey=selected_method,
        defaults={
            "name": selected_method.name,
        },
    )

    invitation, created = Invitation.objects.get_or_create(
        name=request.POST["name"],
        surnames=request.POST["surnames"],
        email=request.POST["email"],
        gender=request.POST["gender"],
        external_survey_invitation=extsurvinv,
    )

    if created:
        return HttpResponse(
            "",
            headers={"HX-Redirect": "/methods/external-surveys?method=" + method_id},
        )

    msg = _("Error creating contact. Contact your network admin.")
    return HttpResponse(
        "",
        headers={
            "HX-Trigger": '{"notification": {"type": "error","text": "' + msg + '"}}',
        },
    )
