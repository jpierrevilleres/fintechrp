from django.http import HttpResponsePermanentRedirect


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
