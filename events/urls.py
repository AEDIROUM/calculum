from django.urls import path, re_path
from . import views

urlpatterns = [
    # Main events list
    path('', views.events, name='events'),
    # Proxy route - must come last to catch remaining patterns
    # Matches: /events/slug and /events/slug/any/path
    re_path(r'^(?P<slug>[\w-]+)/?(?P<path>.*)$', views.event_proxy, name='event_proxy'),
]