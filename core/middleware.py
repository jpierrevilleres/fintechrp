from django.conf import settings
from django.http import HttpResponseForbidden


class AdminIPRestrictionMiddleware:
    """Reject requests to the admin URL that don't originate from allowed IPs.

    Reads `settings.ADMIN_ALLOWED_IPS` and `settings.ADMIN_URL`. Checks the
    request's IP using X-Forwarded-For (if present) falling back to REMOTE_ADDR.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_url = '/' + settings.ADMIN_URL.strip('/') + '/' if settings.ADMIN_URL else '/admin/'
        # Normalize allowed IPs
        self.allowed = set(settings.ADMIN_ALLOWED_IPS or [])

    def __call__(self, request):
        path = request.path
        if path.startswith(self.admin_url):
            # Determine client IP
            xff = request.META.get('HTTP_X_FORWARDED_FOR')
            if xff:
                # X-Forwarded-For may contain multiple IPs
                client_ip = xff.split(',')[0].strip()
            else:
                client_ip = request.META.get('REMOTE_ADDR')

            if client_ip not in self.allowed:
                return HttpResponseForbidden('Access to admin is restricted')

        return self.get_response(request)
