from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from events.models import Event
import requests as http_requests
import logging

logger = logging.getLogger(__name__)


def events(request: HttpRequest) -> HttpResponse:    
    events = Event.objects.prefetch_related('medias').filter(hidden=False).order_by('-title')
    
    return render(
        request,
        'events.html',
        context={
            'events': events
        }
    )


def _get_event_or_error(request, slug):
    """Validate event access. Returns (event, None) or (event, error_response)."""
    event = get_object_or_404(Event, slug=slug)
    
    if not event.server_port:
        return event, render(request, 'event_error.html', {
            'event': event,
            'error_title': 'Serveur non configuré',
            'error_message': f'L\'événement "{event.title}" n\'a pas de serveur configuré.',
        }, status=404)
    
    if not event.is_active:
        return event, render(request, 'event_error.html', {
            'event': event,
            'error_title': 'Serveur inactif',
            'error_message': f'Le serveur pour "{event.title}" est actuellement inactif.',
        }, status=503)
    
    return event, None


@csrf_exempt
def event_proxy(request: HttpRequest, slug: str, path: str = '') -> HttpResponse:
    """
    Hybrid proxy:
    - GET requests use nginx X-Accel-Redirect (handles redirects, URL rewriting, WebSockets)
    - POST/PUT/PATCH/DELETE are proxied directly by Django (nginx X-Accel-Redirect drops the body)
    """
    event, error = _get_event_or_error(request, slug)
    if error:
        return error
    
    prefix = f"/events/{slug}"
    backend_path = f"/{path}" if path and not path.startswith('/') else path or "/"
    
    if request.method == 'GET':
        # Let nginx handle GET — it rewrites redirects, cookies, and HTML
        internal_path = f'/internal-proxy/{slug}/{event.server_port}/{path}'
        if request.META.get('QUERY_STRING'):
            internal_path += f"?{request.META['QUERY_STRING']}"
        response = HttpResponse()
        response['X-Accel-Redirect'] = internal_path
        return response
    
    # POST/PUT/PATCH/DELETE — proxy directly from Django
    target_url = f"http://localhost:{event.server_port}{backend_path}"
    if request.META.get('QUERY_STRING'):
        target_url += f"?{request.META['QUERY_STRING']}"
    
    # Forward headers
    headers = {}
    for key, value in request.META.items():
        if key.startswith('HTTP_') and key not in ('HTTP_HOST', 'HTTP_CONNECTION'):
            headers[key[5:].replace('_', '-')] = value
    if request.META.get('CONTENT_TYPE'):
        headers['Content-Type'] = request.META['CONTENT_TYPE']
    
    # Forward cookies
    if request.META.get('HTTP_COOKIE'):
        headers['Cookie'] = request.META['HTTP_COOKIE']
    
    try:
        resp = http_requests.request(
            method=request.method,
            url=target_url,
            data=request.body,
            headers=headers,
            allow_redirects=False,
            timeout=30,
        )
        
        # Handle redirects — rewrite Location
        if resp.status_code in (301, 302, 303, 307, 308):
            location = resp.headers.get('Location', '')
            if location.startswith('/'):
                location = f"{prefix}{location}"
            django_resp = HttpResponse(status=resp.status_code)
            django_resp['Location'] = location
            _copy_cookies(resp, django_resp)
            return django_resp
        
        django_resp = HttpResponse(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', ''),
        )
        
        _copy_cookies(resp, django_resp)
        return django_resp
        
    except Exception as e:
        logger.error(f'Proxy error for {event.title} ({request.method} {target_url}): {e}')
        return render(request, 'event_error.html', {
            'event': event,
            'error_title': 'Erreur serveur',
            'error_message': f'Impossible de contacter le serveur pour "{event.title}".',
        }, status=502)


def _copy_cookies(resp, django_resp: HttpResponse):
    """Copy Set-Cookie headers from backend to Django response."""
    for name, value in resp.cookies.items():
        django_resp.set_cookie(key=name, value=value)