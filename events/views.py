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


def event_proxy(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Proxy view that forwards requests to the event's configured server.
    Accessible at /events/<slug>
    """
    event = get_object_or_404(Event, slug=slug)
    
    # Check if server is configured and active
    if not event.server_port:
        return HttpResponse(
            f'<h1>No Server Configured</h1>'
            f'<p>The event "{event.title}" does not have a server configured.</p>'
            f'<p><a href="/events">← Back to Events</a></p>',
            status=404
        )
    
    if not event.is_active:
        return HttpResponse(
            f'<h1>Server Inactive</h1>'
            f'<p>The server for "{event.title}" is currently inactive.</p>'
            f'<p><a href="/events">← Back to Events</a></p>',
            status=503
        )
    
    # Build the target URL
    target_url = f"http://localhost:{event.server_port}{request.path_info.replace(f'/events/{slug}', '')}"
    
    # Add query parameters if any
    if request.META.get('QUERY_STRING'):
        target_url += f"?{request.META['QUERY_STRING']}"
    
    try:
        # Forward the request to the backend server
        if request.method == 'GET':
            response = requests.get(target_url, timeout=10, stream=True)
        elif request.method == 'POST':
            response = requests.post(
                target_url,
                data=request.body,
                headers={'Content-Type': request.META.get('CONTENT_TYPE', '')},
                timeout=10,
                stream=True
            )
        else:
            # Support other HTTP methods if needed
            response = requests.request(
                method=request.method,
                url=target_url,
                data=request.body,
                headers={'Content-Type': request.META.get('CONTENT_TYPE', '')},
                timeout=10,
                stream=True
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
        return HttpResponse(
            f'<h1>Server Offline</h1>'
            f'<p>Unable to connect to the server for "{event.title}" on port {event.server_port}.</p>'
            f'<p>The server may be down or not running.</p>'
            f'<p><a href="/events">← Back to Events</a></p>',
            status=503
        )
    except requests.exceptions.Timeout:
        return HttpResponse(
            f'<h1>Server Timeout</h1>'
            f'<p>The server for "{event.title}" took too long to respond.</p>'
            f'<p><a href="/events">← Back to Events</a></p>',
            status=504
        )
    except Exception as e:
        return HttpResponse(
            f'<h1>Server Error</h1>'
            f'<p>An error occurred while connecting to the server for "{event.title}".</p>'
            f'<p>Error: {str(e)}</p>'
            f'<p><a href="/events">← Back to Events</a></p>',
            status=500
        )