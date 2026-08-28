from django.core.cache import cache
from django.http import HttpResponse

# Paths bots commonly probe for on every Django/PHP/WordPress site.
# None of these exist here, so reject them immediately without
# routing, views, or the ORM ever getting involved.
SUSPICIOUS_PATH_FRAGMENTS = (
    '.env', '.git', 'wp-login', 'wp-admin', 'wp-content', 'phpmyadmin',
    '.aws', 'xmlrpc.php', '.php', '.sql', 'wallet.dat', 'config.json',
    '.well-known/security.txt',
)


class BotShieldMiddleware:
    """
    Dependency-free protection against scanner/bot traffic.

    Placed right after WhiteNoise in MIDDLEWARE so static file requests
    never reach it, and everything else is filtered before it costs
    anything (URL resolution, views, database).

    Rate limit state lives in Django's cache (see CACHES in settings,
    using a file-based cache so it's shared across gunicorn workers).
    """

    RATE_LIMIT = 120   # requests
    RATE_WINDOW = 60   # seconds

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.lower()
        if any(fragment in path for fragment in SUSPICIOUS_PATH_FRAGMENTS):
            return HttpResponse(status=404)

        ip = self._client_ip(request)
        cache_key = f'botshield:{ip}'
        count = cache.get(cache_key)
        if count is None:
            cache.set(cache_key, 1, timeout=self.RATE_WINDOW)
        elif count >= self.RATE_LIMIT:
            return HttpResponse('Too Many Requests', status=429)
        else:
            try:
                cache.incr(cache_key)
            except ValueError:
                cache.set(cache_key, 1, timeout=self.RATE_WINDOW)

        return self.get_response(request)

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
