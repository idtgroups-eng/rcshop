from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed = ["/login/","/verify-otp/","/add-address/","/admin/"]

        if not request.session.get("customer_id") and not any(request.path.startswith(a) for a in allowed):
            return redirect("/login/")

        return self.get_response(request)
