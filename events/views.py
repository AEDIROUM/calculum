from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from events.models import Event


def events(request: HttpRequest) -> HttpResponse:    
    events = Event.objects.prefetch_related('medias').filter(hidden=False).order_by('-title')
    
    return render(
        request,
        'events.html',
        context={
            'events': events
        }
    )


def event_proxy(request: HttpRequest, slug: str, path: str = '') -> HttpResponse:
    """
    Proxy view that uses nginx X-Accel-Redirect for robust proxying.
    Django controls access (slug lookup, is_active check).
    nginx handles everything else: redirects, cookies, WebSockets, URL rewriting.
    """
    event = get_object_or_404(Event, slug=slug)
    
    if not event.server_port:
        return render(request, 'event_error.html', {
            'event': event,
            'error_title': 'Serveur non configuré',
            'error_message': f'L\'événement "{event.title}" n\'a pas de serveur configuré.',
        }, status=404)
    
    if not event.is_active:
        return render(request, 'event_error.html', {
            'event': event,
            'error_title': 'Serveur inactif',
            'error_message': f'Le serveur pour "{event.title}" est actuellement inactif.',
        }, status=503)
    
    # Pass slug in the internal path so nginx can rewrite redirects and URLs
    internal_path = f'/internal-proxy/{slug}/{event.server_port}/{path}'
    if request.META.get('QUERY_STRING'):
        internal_path += f"?{request.META['QUERY_STRING']}"
    
    response = HttpResponse()
    response['X-Accel-Redirect'] = internal_path
    return response