from django.conf import settings
from django.http import HttpResponseForbidden


class FixDuplicateHostHeaderMiddleware:
    """Fix duplicate Host headers from CloudFront/ALB chain.
    
    When CloudFront forwards requests to ALB and both add Host headers,
    we get 'host1,host2' which violates RFC 1034/1035.
    This middleware cleans up the Host header before Django processes it.
    
    Also ensures Django uses the correct host for redirects by preferring
    X-Forwarded-Host over the raw Host header.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Fix duplicate Host header (comma-separated values)
        http_host = request.META.get('HTTP_HOST', '')
        if ',' in http_host:
            # Take the first host value
            http_host = http_host.split(',')[0].strip()
            request.META['HTTP_HOST'] = http_host
        
        # Use X-Forwarded-Host if present (from CloudFront/ALB)
        # This ensures redirects use the public domain, not the ALB domain
        x_forwarded_host = request.META.get('HTTP_X_FORWARDED_HOST', '')
        if x_forwarded_host:
            if ',' in x_forwarded_host:
                x_forwarded_host = x_forwarded_host.split(',')[0].strip()
            request.META['HTTP_HOST'] = x_forwarded_host
        
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
