from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from events.models import Event
import requests
from urllib.parse import urljoin


def events(request: HttpRequest) -> HttpResponse:    
    events = Event.objects.prefetch_related('medias').all().order_by('-title')
    
    return render(
        request,
        'events.html',
        context={
            'events': events
        }
    )


def event_proxy(request: HttpRequest, slug: str, path: str = '') -> HttpResponse:
    """
    Proxy view that forwards requests to the event's configured server.
    Accessible at /events/<slug> and /events/<slug>/any/path
    """
    event = get_object_or_404(Event, slug=slug)
    
    # Check if server is configured and active
    if not event.server_port:
        return render(request, 'event_error.html', {
            'title': 'Aucun serveur configuré',
            'message': f'L\'événement "{event.title}" n\'a pas de serveur configuré.',
            'event': event
        }, status=404)
    
    if not event.is_active:
        return render(request, 'event_error.html', {
            'title': 'Serveur inactif',
            'message': f'Le serveur pour "{event.title}" est actuellement inactif.',
            'event': event
        }, status=503)
    
    # Build the target URL
    # Add leading slash to path if it doesn't have one
    if path and not path.startswith('/'):
        path = '/' + path
    
    target_url = f"http://localhost:{event.server_port}{path}"
    
    # Add query parameters if any
    if request.META.get('QUERY_STRING'):
        target_url += f"?{request.META['QUERY_STRING']}"
    
    try:
        # Forward the request to the backend server
        if request.method == 'GET':
            response = requests.get(target_url, timeout=10, stream=True, allow_redirects=True)
        elif request.method == 'POST':
            response = requests.post(
                target_url,
                data=request.body,
                headers={'Content-Type': request.META.get('CONTENT_TYPE', '')},
                timeout=10,
                stream=True,
                allow_redirects=True
            )
        else:
            # Support other HTTP methods if needed
            response = requests.request(
                method=request.method,
                url=target_url,
                data=request.body,
                headers={'Content-Type': request.META.get('CONTENT_TYPE', '')},
                timeout=10,
                stream=True,
                allow_redirects=True
            )
        
        # Create Django response from proxied response
        django_response = StreamingHttpResponse(
            response.iter_content(chunk_size=8192),
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'text/html')
        )
        
        # Copy relevant headers
        for header in ['Content-Type', 'Content-Length', 'Cache-Control']:
            if header in response.headers:
                django_response[header] = response.headers[header]
        
        return django_response
        
    except requests.exceptions.ConnectionError:
        return render(request, 'event_error.html', {
            'title': 'Serveur hors ligne',
            'message': f'Impossible de se connecter au serveur pour "{event.title}" sur le port {event.server_port}.',
            'detail': 'Le serveur est peut-être éteint ou ne fonctionne pas.',
            'event': event
        }, status=503)
        
    except requests.exceptions.Timeout:
        return render(request, 'event_error.html', {
            'title': 'Délai d\'attente dépassé',
            'message': f'Le serveur pour "{event.title}" a mis trop de temps à répondre.',
            'event': event
        }, status=504)
        
    except Exception as e:
        return render(request, 'event_error.html', {
            'title': 'Erreur du serveur',
            'message': f'Une erreur s\'est produite lors de la connexion au serveur pour "{event.title}".',
            'detail': str(e),
            'event': event
        }, status=500)