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
    Django controls access, nginx does the actual proxying.
    """
    event = get_object_or_404(Event, slug=slug)
    
    # Check if server is configured and active
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
    
    # Use nginx internal redirect for robust proxying
    # nginx handles: cookies, WebSockets, all HTTP methods, file uploads, etc.
    internal_path = f'/internal-proxy/{event.server_port}/{path}'
    
    response = HttpResponse()
    response['X-Accel-Redirect'] = internal_path
    
    # Pass through query string
    if request.META.get('QUERY_STRING'):
        response['X-Accel-Redirect'] += f"?{request.META['QUERY_STRING']}"
    
    return response