from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from board.models import Meet


def cheatsheet(request: HttpRequest) -> HttpResponse:
    meets = Meet.objects.all().order_by('date')
    
    algos = []
    for meet in meets:
        algo_content = meet.get_algo_content()
        # Only include files with actual code (not just comments/blanks)
        if algo_content and algo_content.strip():
            algos.append({
                'theme': meet.theme or f"Rencontre {meet.date.strftime('%d/%m/%Y')}",
                'content': algo_content
            })
    
    return render(
        request, 
        'cheatsheet.html', 
        context={'algos': algos}
    )