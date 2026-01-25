from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from board.models import Meet, Session
from datetime import datetime
import re


def board(request: HttpRequest):
    meets = Meet.objects.select_related('session').prefetch_related('problems').all()
    
    # Get all sessions
    sessions = Session.objects.all().order_by('-year', 'season')
    
    # Determine current session
    now = datetime.now()
    month = now.month
    year = now.year
    
    if 9 <= month <= 12:
        current_season = 'autumn'
    elif 1 <= month <= 4:
        current_season = 'winter'
    else:
        current_season = 'summer'
    
    # Get selected session from query param or use current/last
    selected_session_id = request.GET.get('session')
    
    if selected_session_id:
        try:
            selected_session = Session.objects.get(id=selected_session_id)
        except Session.DoesNotExist:
            selected_session = None
    else:
        # Try to find current session
        selected_session = Session.objects.filter(
            season=current_season, 
            year=year
        ).first()
        
        # If current doesn't exist, get the most recent
        if not selected_session:
            selected_session = sessions.first()
    
    # Get meets for selected session
    session_meets = []
    if selected_session:
        session_meets = meets.filter(session=selected_session)
        
        # Extract problem titles and sort problems by __str__
        for meet in session_meets:
            problems = list(meet.problems.all())
            for problem in problems:
                match = re.search(r'/problems?/([^/?]+)', problem.link)
                if match:
                    title = match.group(1).replace('-', ' ').replace('_', ' ')
                    problem.extracted_title = title
                else:
                    problem.extracted_title = None
            # Sort problems by their __str__
            problems.sort(key=lambda p: str(p))
            meet.sorted_problems = problems
    
    return render(
        request,
        'board.html',
        context={
            'sessions': sessions,
            'selected_session': selected_session,
            'meets': session_meets,
            'has_meets': len(session_meets) > 0
        }
    )