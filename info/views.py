from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def presentation(request: HttpRequest) -> HttpResponse:
    return render(request, 'presentation.html')

def noob(request: HttpRequest) -> HttpResponse:
    return render(request, 'noob.html')
