from django.shortcuts import redirect


class SuperadminRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if "superadmin" in path:
            user = getattr(request, "user", None)
            if user and user.is_authenticated:
                if user.is_superuser and user.is_active:
                    return self.get_response(request)
                else:
                    return redirect("/admin")
            else:
                return redirect("/")

        return self.get_response(request)
