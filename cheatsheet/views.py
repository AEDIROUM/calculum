from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from cheatsheet.models import Algorithm, AlgorithmCategory


def cheatsheet(request: HttpRequest) -> HttpResponse:
    """Display all algorithms organized by category"""
    
    # Get categories with their algorithms, sorted alphabetically
    categories = AlgorithmCategory.objects.prefetch_related('algorithms').order_by('name')
    
    # Also get algorithms without a category
    uncategorized = Algorithm.objects.filter(category__isnull=True).order_by('title')
    
    context = {
        'categories': categories,
        'uncategorized': uncategorized,
        'has_algorithms': Algorithm.objects.exists()
    }
    
    return render(request, 'cheatsheet.html', context=context)