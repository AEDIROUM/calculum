from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from events.models import Event
import requests as http_requests
import logging
import re

logger = logging.getLogger(__name__)

_HOP_BY_HOP = frozenset({
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade',
})


def events(request: HttpRequest) -> HttpResponse:
    visible = Event.objects.prefetch_related('medias').filter(hidden=False).order_by('-title')
    return render(request, 'events.html', context={'events': visible})


@csrf_exempt
def event_proxy(request: HttpRequest, slug: str, path: str = '') -> HttpResponse:
    """Reverse proxy — every HTTP method goes through Django."""
    event = get_object_or_404(Event, slug=slug)

    if not event.server_port:
        return _error(request, event, 'Serveur non configuré',
                      f"L'événement « {event.title} » n'a pas de serveur configuré.", 404)

    if not event.is_active:
        return _error(request, event, 'Serveur inactif',
                      f"Le serveur pour « {event.title} » est actuellement inactif.", 503)

    prefix = f'/events/{slug}'
    target = f'http://localhost:{event.server_port}/{path}'
    qs = request.META.get('QUERY_STRING')
    if qs:
        target += f'?{qs}'

    headers = _build_headers(request)

    try:
        upstream = http_requests.request(
            method=request.method,
            url=target,
            data=request.body or None,
            headers=headers,
            allow_redirects=False,
            timeout=30,
        )
    except http_requests.ConnectionError:
        return _error(request, event, 'Erreur de connexion',
                      f"Impossible de contacter le serveur pour « {event.title} ».", 502)
    except Exception as exc:
        logger.error('Proxy %s %s → %s', request.method, target, exc)
        return _error(request, event, 'Erreur serveur',
                      f"Erreur inattendue pour « {event.title} ».", 502)

    # Redirects — rewrite Location
    backend_origin = re.compile(rf'^https?://localhost:{event.server_port}')
    if upstream.status_code in (301, 302, 303, 307, 308):
        location = upstream.headers.get('Location', '')
        # Strip absolute backend origin → relative path
        location = backend_origin.sub('', location)
        if not location:
            location = prefix + '/'
        elif location.startswith('/'):
            location = prefix + location
        resp = HttpResponse(status=upstream.status_code)
        resp['Location'] = location
        _forward_cookies(upstream, resp, prefix)
        return resp

    # Body — rewrite URLs in HTML, JS, and CSS responses
    ct = upstream.headers.get('Content-Type', '')
    body = _rewrite_body(upstream, ct, prefix, event.server_port)

    resp = HttpResponse(body, status=upstream.status_code, content_type=ct)

    # Forward safe response headers (skip hop-by-hop + headers Django manages)
    for key, value in upstream.headers.items():
        if key.lower() not in _HOP_BY_HOP | {
            'content-type', 'content-encoding', 'content-length', 'set-cookie',
        }:
            resp[key] = value

    _forward_cookies(upstream, resp, prefix)
    return resp


# ─── Helpers ─────────────────────────────────────────────────────────────

def _build_headers(request: HttpRequest) -> dict:
    """Extract forwarding headers from the incoming Django request."""
    headers = {}
    for k, v in request.META.items():
        if k.startswith('HTTP_') and k not in ('HTTP_HOST', 'HTTP_CONNECTION'):
            name = k[5:].replace('_', '-')
            if name.lower() not in _HOP_BY_HOP:
                headers[name] = v
    ct = request.META.get('CONTENT_TYPE')
    if ct:
        headers['Content-Type'] = ct
    return headers


def _forward_cookies(upstream, resp: HttpResponse, prefix: str):
    """Parse raw Set-Cookie headers and re-emit them with the proxy path."""
    for raw in upstream.raw.headers.getlist('Set-Cookie'):
        parts = raw.split(';')
        if not parts or '=' not in parts[0]:
            continue
        name, value = parts[0].strip().split('=', 1)
        kw: dict = {'key': name, 'value': value, 'path': f'{prefix}/'}
        for attr in parts[1:]:
            attr = attr.strip()
            if not attr:
                continue
            if '=' in attr:
                a, v = attr.split('=', 1)
                a, v = a.strip().lower(), v.strip()
                if a == 'domain':
                    kw['domain'] = v
                elif a == 'max-age':
                    try:
                        kw['max_age'] = int(v)
                    except ValueError:
                        pass
                elif a == 'expires':
                    kw['expires'] = v
                elif a == 'samesite':
                    kw['samesite'] = v
            else:
                a = attr.lower()
                if a == 'secure':
                    kw['secure'] = True
                elif a == 'httponly':
                    kw['httponly'] = True
        resp.set_cookie(**kw)


def _rewrite_body(upstream, ct: str, prefix: str, port: int):
    """Pick the right rewriter based on Content-Type."""
    if 'text/html' in ct:
        return _rewrite_urls(upstream.text, prefix, port)
    if 'javascript' in ct:
        return _rewrite_urls(upstream.text, prefix, port)
    if 'text/css' in ct:
        return _rewrite_urls(upstream.text, prefix, port)
    return upstream.content


def _rewrite_urls(text: str, prefix: str, port: int) -> str:
    """
    Rewrite URLs in any text content (HTML, JS, CSS).
    1. Replace absolute backend URLs (http(s)://localhost:PORT/...) with prefixed paths
    2. Replace root-relative paths (/...) with prefixed paths
    """
    # Step 1: absolute backend URLs → prefixed path
    text = re.sub(rf'https?://localhost:{port}(/[^"\s\'<>)]*)', rf'{prefix}\1', text)
    text = re.sub(rf'https?://localhost:{port}(["\'])', rf'{prefix}/\1', text)
    # Step 2: HTML attributes with root-relative paths
    text = re.sub(r'((?:href|src|action)\s*=\s*")(/[^"]*)"', rf'\1{prefix}\2"', text)
    text = re.sub(r"((?:href|src|action)\s*=\s*')(/[^']*?)'", rf"\1{prefix}\2'", text)
    # Step 3: CSS url()
    text = re.sub(r"url\(\s*'(/[^']*?)'\s*\)", rf"url('{prefix}\1')", text)
    text = re.sub(r'url\(\s*"(/[^"]*?)"\s*\)', rf'url("{prefix}\1")', text)
    text = re.sub(r'url\(\s*(/[^)\s]+)\s*\)', rf'url({prefix}\1)', text)
    # Step 4: JS string literals with root-relative paths (not already prefixed)
    text = re.sub(r"'(/(?!events/)[^'\n]+)'", rf"'{prefix}\1'", text)
    text = re.sub(r'"(/(?!events/)[^"\n]+)"', rf'"{prefix}\1"', text)
    text = re.sub(r'`(/(?!events/)[^`\n]+)`', rf'`{prefix}\1`', text)
    return text


def _error(request, event, title, message, status):
    return render(request, 'event_error.html', {
        'event': event, 'error_title': title, 'error_message': message,
    }, status=status)