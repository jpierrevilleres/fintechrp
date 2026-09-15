from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponsePermanentRedirect


class RedirectWWWMiddleware:
    """Redirect www.fintechrp.com to fintechrp.com (canonical domain)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().lower()
        
        # Redirect www to non-www
        if host.startswith('www.'):
            new_host = host[4:]  # Remove 'www.'
            new_url = f"{request.scheme}://{new_host}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(new_url)
        
        return self.get_response(request)


class FixDuplicateHostHeaderMiddleware:
    """Fix duplicate Host headers from CloudFront/ALB chain.
    
    When CloudFront/ALB add duplicate headers, we get 'host1,host2' which 
    violates RFC 1034/1035. This middleware cleans up duplicate headers.
    
    With USE_X_FORWARDED_HOST=True in settings, Django will automatically use 
    X-Forwarded-Host from ALB (which contains the original viewer domain).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Fix duplicate Host header (comma-separated values)
        http_host = request.META.get('HTTP_HOST', '')
        if ',' in http_host:
            request.META['HTTP_HOST'] = http_host.split(',')[0].strip()
        
        # Fix duplicate X-Forwarded-Host header if present
        x_fwd_host = request.META.get('HTTP_X_FORWARDED_HOST', '')
        if ',' in x_fwd_host:
            request.META['HTTP_X_FORWARDED_HOST'] = x_fwd_host.split(',')[0].strip()
        
        return self.get_response(request)


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
