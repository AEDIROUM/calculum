from django.urls import path, re_path
from . import views

urlpatterns = [
    path('/', views.events, name='events'),
    # Proxy route - catches /events/<slug> and optionally /events/<slug>/path
    # The trailing slash and anything after is optional
    re_path(r'^(?P<slug>[\w-]+)/?(?P<path>.*)$', views.event_proxy, name='event_proxy'),
]