import ipaddress

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

    Reads `settings.ADMIN_ALLOWED_IPS`, `settings.ADMIN_PROXY_HOPS` and
    `settings.ADMIN_URL`. Checks the request's IP using X-Forwarded-For (if
    present, counted from the right) falling back to REMOTE_ADDR.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_url = '/' + settings.ADMIN_URL.strip('/') + '/' if settings.ADMIN_URL else '/admin/'
        # Entries may be single IPs or CIDR ranges (e.g. '213.55.218.0/24'),
        # since a residential ISP reassigns addresses within its block
        self.allowed = [
            ipaddress.ip_network(entry.strip(), strict=False)
            for entry in (settings.ADMIN_ALLOWED_IPS or [])
        ]

    def _is_allowed(self, client_ip):
        try:
            ip = ipaddress.ip_address(client_ip)
        except (TypeError, ValueError):
            return False
        return any(ip in network for network in self.allowed)

    def __call__(self, request):
        path = request.path
        if path.startswith(self.admin_url):
            # Determine client IP. CloudFront *appends* the viewer IP to any
            # X-Forwarded-For the client sends, so the leftmost entries are
            # attacker-controlled. Count from the right instead: each of our
            # proxies appends one entry (CloudFront: viewer IP, ALB: CloudFront
            # IP, nginx: ALB IP), so the real client is ADMIN_PROXY_HOPS from
            # the end. Too few entries means the request skipped a proxy.
            xff = request.META.get('HTTP_X_FORWARDED_FOR')
            if xff:
                hops = [part.strip() for part in xff.split(',') if part.strip()]
                proxy_hops = settings.ADMIN_PROXY_HOPS
                client_ip = hops[-proxy_hops] if len(hops) >= proxy_hops else None
            else:
                client_ip = request.META.get('REMOTE_ADDR')

            if not self._is_allowed(client_ip):
                return HttpResponseForbidden('Access to admin is restricted')

        return self.get_response(request)


class NoStoreCacheMiddleware:
    """Mark every Django-rendered response as not cacheable.

    This is a dynamic site (per-session CSRF tokens, messages framework,
    search/filter results driven by query strings) - CloudFront was
    observed caching /articles/ and replaying that single cached copy
    for every ?q= search variation, since its cache policy ignores query
    strings when building the cache key. This doesn't fix that cache
    policy (needs an AWS console change), but it's the correct signal to
    send regardless, and helps if the policy is ever set to respect
    origin cache headers. Static assets are unaffected - nginx serves
    /static/ and /media/ directly, never reaching this middleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-store'
        return response
