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
    Accessible at /events/<slug> or /events/<slug>/path
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
    
    # Build the target URL - add leading slash to path if not empty
    backend_path = f"/{path}" if path and not path.startswith('/') else path or "/"
    target_url = f"http://localhost:{event.server_port}{backend_path}"
    
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
        
        # For HTML responses, we need to rewrite URLs
        content_type = response.headers.get('Content-Type', '')
        
        if 'text/html' in content_type:
            # Read the full HTML content
            html_content = response.content.decode('utf-8', errors='ignore')
            
            # Rewrite absolute paths to be relative to /events/<slug>/
            import re
            
            # Fix href and src attributes that start with /
            # Change href="/css/..." to href="/events/<slug>/css/..."
            html_content = re.sub(
                r'(href|src)="(/[^"]*)"',
                rf'\1="/events/{slug}\2"',
                html_content
            )
            
            # Also fix action attributes for forms
            html_content = re.sub(
                r'action="(/[^"]*)"',
                rf'action="/events/{slug}\1"',
                html_content
            )
            
            # Create response with modified HTML
            django_response = HttpResponse(
                html_content,
                status=response.status_code,
                content_type=content_type
            )
        else:
            # For non-HTML (CSS, JS, images, etc.), just stream it
            django_response = StreamingHttpResponse(
                response.iter_content(chunk_size=8192),
                status=response.status_code,
                content_type=content_type
            )
        
        # Copy relevant headers
        for header in ['Content-Type', 'Cache-Control']:
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