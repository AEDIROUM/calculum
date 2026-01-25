from django.shortcuts import render

def presentation(request):
    return render(request, 'presentation.html')

def noob(request):
    return render(request, 'noob.html')
