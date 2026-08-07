import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.db.models import Prefetch, Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import ListView, TemplateView
from unfold.views import UnfoldModelAdminViewMixin

from apps.geodata.models import Region1
from apps.methods.forms import InvitationCreationForm
from apps.methods.mixins import MethodFillMixin
from project.utils.mixins import NetworkFilterMixin

from .helpers import (
    ParseExternalInvitations,
    get_external_survey_filter,
    get_form_sections,
    get_survey_stats,
)
from .models import Campaign, ExternalSurveyInvitation, Invitation, Method, Survey
from .services import (
    send_invitation,
    send_survey_reminder_email,
    send_user_survey_reminder_email,
)


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
        invitations = Invitation.objects.none()
        selected_method_id = kwargs["method_id"]
        organization_id = kwargs["organization_id"]
        campaign_id = kwargs["campaign_id"]
        selected_ext_survey_id = self.request.GET.get("ext_survey")
        external_survey_invitation_id = None

        # Get all the external surveys of the current method
        method = Method.objects.get(
            id=selected_method_id,
        )
        ext_surveys = method.external_surveys.all()

        if selected_ext_survey_id:
            selected_ext_survey = ext_surveys.filter(id=selected_ext_survey_id).first()
        else:
            selected_ext_survey = ext_surveys.first()

        if selected_ext_survey:
            external_survey_invitation = ExternalSurveyInvitation.objects.filter(
                external_survey=selected_ext_survey,
                organization=organization_id,
                campaign=campaign_id,
            ).first()

            if external_survey_invitation:
                invitations = Invitation.objects.filter(
                    external_survey_invitation=external_survey_invitation
                )
                external_survey_invitation_id = external_survey_invitation.id

        context.update(
            {
                "method": method,
                "ext_surveys": ext_surveys,
                "selected_ext_survey": selected_ext_survey,
                "invitations": invitations,
                "create_invitation_form": InvitationCreationForm,
                "organization_id": organization_id,
                "campaign_id": campaign_id,
                "external_survey_invitation_id": external_survey_invitation_id,
            }
        )

        return context


@require_POST
def delete_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    invitation.delete()
    return HttpResponse("")


@method_decorator(login_not_required, name="dispatch")
class ExternalMethodFillView(MethodFillMixin, TemplateView):
    template_name = "methods/method_fill.html"

    def get_context_data(self, **kwargs):
        invitation = Invitation.objects.get(token=self.kwargs["token"])

        kwargs["campaign_id"] = invitation.external_survey_invitation.campaign.id
        kwargs["method"] = invitation.external_survey_invitation.external_survey
        return super().get_context_data(**kwargs)

    def post(self, request, token):
        action = request.POST.get("action")
        invitation = Invitation.objects.get(token=token)
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
            send_invitation(request, invitation)
            invitation.status = Invitation.Status.SENT
            invitation.send_date = timezone.now()
            invitation.save()

        msg = _("The invitations have been sent.")
    else:
        msg = _("There are no invitations to send.")

    if "superadmin" in request.META.get("HTTP_REFERER", "/"):
        messages.success(
            request,
            msg,
        )

        return redirect(request.META.get("HTTP_REFERER", "/"))
    else:
        return HttpResponse(
            render(
                request,
                "components/methods/invitations_table.html",
                {
                    "invitations": Invitation.objects.filter(
                        external_survey_invitation_id=id
                    )
                },
            ),
            headers={
                "HX-Trigger": '{"notification": {"type": "success","text": "'
                + msg
                + '"}}',
            },
        )


def invitation_sent_view(request, id):
    invitation = Invitation.objects.get(pk=id)
    send_invitation(request, invitation)
    invitation.status = Invitation.Status.SENT
    invitation.send_date = timezone.now()
    invitation.save()

    if "superadmin" in request.META.get("HTTP_REFERER", "/"):
        messages.success(
            request,
            _("The invitation has been sent."),
        )

        return redirect(request.META.get("HTTP_REFERER", "/"))
    else:
        msg = _("The invitation has been sent.")

        return HttpResponse(
            render(
                request,
                "components/methods/invitation_row.html",
                {"invitation": invitation},
            ),
            headers={
                "HX-Trigger": '{"notification": {"type": "success","text": "'
                + msg
                + '"}}',
            },
        )


def import_csv(request, organization_id, method_id, campaign_id):
    # The method_id comes from the method of type external invitation
    extsurvinv = create_external_survey_invitation(
        organization_id, method_id, campaign_id
    )

    if request.method == "POST":
        csv_file = request.FILES["csv_file"] if "csv_file" in request.FILES else False

        message_type = "error"
        result = {"error_messages": "", "invitations": []}
        displayed_message = ""
        if csv_file:
            decoded_file = csv_file.read().decode("utf-8-sig").splitlines()
            reader = csv.reader(decoded_file)
            pei = ParseExternalInvitations()
            result = pei.parse_csv(reader, extsurvinv.id)

            if len(result["error_messages"]) > 0:
                displayed_message = "\n".join(result["error_messages"])
            else:
                displayed_message = _("The CSV has been imported correctly.")
                message_type = "success"
        else:
            displayed_message = _("There is no CSV file selected to import.")

        return HttpResponse(
            render(
                request,
                "components/methods/invitations_imported_rows.html",
                {"invitationsImported": result["invitations"]},
            ),
            headers={
                "HX-Trigger": '{"notification": {"type": "'
                + message_type
                + '","text": "'
                + displayed_message
                + '"}}',
            },
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

    def get_queryset(self):
        all_surveys = Survey.objects.filter(self.get_survey_query(self.request.GET))

        all_surveys = self.filter_queryset_by_network(self.request, all_surveys)
        return (
            all_surveys.select_related("method")
            .prefetch_related(Prefetch("method__external_surveys"))
            .order_by(self.get_survey_order())
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        page = context["page_obj"]
        processed = []
        for s in page.object_list:
            s.status = Survey.Status(s.status).value
            s.method.sections = get_form_sections(s.method)
            s.method.external_surveys_c = get_external_surveys(s.method)

            stats = get_survey_stats(s, s.method, s.campaign)
            s.totalProgress = stats["totalProgress"]
            processed.append(s)

        all_status = []
        for s in Survey.Status:
            all_status.append({"id": s.value, "name": s.label})
        unit_of_analysis = []
        for ua in Method.UnitAnalysis:
            unit_of_analysis.append({"id": ua.value, "name": ua.label})

        campaigns = Campaign.objects.filter(status=True)
        for c in campaigns:
            c.name = f"{c.name} | {c.year}"

        methods = Method.objects.filter(campaign_methods__status=True).distinct()
        methods = self.filter_queryset_by_network(self.request, methods)

        context["campaigns"] = campaigns
        context["regions"] = Region1.objects.all()
        context["methods"] = methods
        context["unitanalysis"] = unit_of_analysis
        context["status"] = all_status
        context["language"] = get_language()

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

    def get_survey_order(self):
        order = self.request.GET.get("o")
        if not order:
            order = "-start_date"
        return order


def create_external_survey_invitation(organization_id, method_id, campaign_id):
    if not method_id:
        return HttpResponseBadRequest("Missing method_id")

    ext_survey_method = get_object_or_404(
        Method,
        id=method_id,
        unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY,
    )

    extsurvinv, _ = ExternalSurveyInvitation.objects.get_or_create(
        external_survey=ext_survey_method,
        organization_id=organization_id,
        campaign_id=campaign_id,
        defaults={
            "name": ext_survey_method.name,
        },
    )
    return extsurvinv


@require_http_methods("POST")
def create_invitation_action(request):
    method_id = request.POST.get("method_id")
    ext_survey_id = request.POST.get("ext_survey_id")
    organization_id = request.POST.get("organization_id")
    campaign_id = request.POST.get("campaign_id")
    extsurvinv = create_external_survey_invitation(
        organization_id, ext_survey_id, campaign_id
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
            headers={
                "HX-Redirect": reverse(
                    "methods:external_surveys_view",
                    args=[organization_id, method_id, campaign_id],
                )
                + f"?ext_survey={ext_survey_id}"
            },
        )

    msg = _("Error creating contact. Contact your network admin.")
    return HttpResponse(
        "",
        headers={
            "HX-Trigger": '{"notification": {"type": "error","text": "' + msg + '"}}',
        },
    )


def survey_reminder_view(request):
    send_survey_reminder_email(request)
    messages.success(
        request,
        _("An email to all the involved contacts has been sent."),
    )
    return redirect(request.META.get("HTTP_REFERER", "/"))


def user_survey_reminder_view(request, survey_id):
    send_user_survey_reminder_email(request, survey_id)
    messages.success(
        request,
        _("An email to the contact has been sent."),
    )
    return redirect(request.META.get("HTTP_REFERER", "/"))


def get_external_surveys(method):
    ext_surveys_type = {
        Method.ExternalSurveyCategory.ASSOCIATIVE: 0,
        Method.ExternalSurveyCategory.PROFESSIONAL: 0,
        Method.ExternalSurveyCategory.VOLUNTEERING: 0,
        Method.ExternalSurveyCategory.WORK: 0,
    }
    for ext_survey in method.external_surveys.all():
        ext_surveys_type[ext_survey.external_survey_category] += 1

    return ext_surveys_type


class MethodFillSuccessView(TemplateView):
    template_name = "methods/fill_success.html"
