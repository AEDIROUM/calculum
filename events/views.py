from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from events.models import Event


def events(request: HttpRequest) -> HttpResponse:    
    events = Event.objects.prefetch_related('medias').all().order_by('-title')
    
    return render(
        request,
        'events.html',
        context={
            'events': events
        }
    )