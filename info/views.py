
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from board.models import Session

def presentation(request: HttpRequest) -> HttpResponse:
    last_session = Session.objects.order_by('-year', 'season').first()
    return render(request, 'presentation.html', {'last_session': last_session})

def noob(request: HttpRequest) -> HttpResponse:
    return render(request, 'noob.html')
