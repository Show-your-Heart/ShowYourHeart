from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils.translation import activate, get_language
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView, TemplateView

from apps.organizations.models import Organization


class RootRedirectView(RedirectView):
    """
    This view captures the requests that don't include any path in the URL,
    like "http://localhost:1234/"

    It's meant to handle the language detection and to redirect to the
    language that django detects from the browser.

    This can normally be hanmdled by Django itself with a middleware
    django.middleware.locale.LocaleMiddleware
    But for some reason that I (Pere) don't remember, I had to make this view.

    Maybe it was some bug that in current Django versions doesn't happen
    anymore.
    """

    url = reverse_lazy("home")

    def get_redirect_url(self, *args, **kwargs):
        activate(get_language())
        return super().get_redirect_url(*args, **kwargs)


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        method_list = []
        organization_accepted = False
        if hasattr(self.request.user, "profile"):
            organization_accepted = (
                self.request.user.profile.organization.status
                == Organization.Status.ACCEPTED
            )
            for method in self.request.user.profile.organization.methods.all():
                method_list.append({"id": method.id, "name": method.name})

        add_context = {
            "user": self.request.user,
            "organization": self.request.user.profile.organization,
            "available_methods": method_list,
            "organization_accepted": organization_accepted,
        }
        context.update(add_context)
        return context


class StandardSuccess(TemplateView):
    template_name = "standard_success.html"
    link_text = _("Back")
    page_title = _("Registry updated")
    title = _("Registry successfully updated")
    success_title = _("Done!")
    description = _("The registry was updated correctly.")
    url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_context = {
            "link_text": self.get_link_text(),
            "page_title": self.page_title,
            "title": self.title,
            "success_title": self.success_title,
            "description": self.description,
            "url": self.get_url(),
        }
        context.update(add_context)
        return context

    def get_url(self):
        try:
            reversed_url = reverse(self.url)
        except NoReverseMatch:
            return self.url
        return reversed_url

    def get_link_text(self):
        return self.link_text
