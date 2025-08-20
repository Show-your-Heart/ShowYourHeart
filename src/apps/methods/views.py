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

from apps.methods.mixins import CommonContextMixin

from .helpers import ParseExternalInvitations, get_external_survey_filter
from .models import Campaign, Invitation, Method
from .services import send_invitation


class MethodFillView(CommonContextMixin, TemplateView):
    template_name = "methods/method_fill.html"

    def get_context_data(self, **kwargs):
        method = Method.objects.get(pk=self.kwargs["id"])
        kwargs["campaign"] = Campaign.objects.get(methods__id__contains=method.id).id
        kwargs["method"] = method
        return super().get_context_data(**kwargs)

    def post(self, request, id):
        method_id = id
        try:
            campaign = Campaign.objects.get(methods__id__contains=method_id)
        except ObjectDoesNotExist as error:
            raise ObjectDoesNotExist(
                _("The method has no asociated campaign and can't be answered")
            ) from error

        return super().post(request, method_id, campaign.id)


@method_decorator(login_not_required, name="dispatch")
class ExternalMethodFillView(CommonContextMixin, TemplateView):
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
