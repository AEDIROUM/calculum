from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.events, name='events'),
    # Proxy route - catches /events/<slug> and everything after it
    re_path(r'^(?P<slug>[\w-]+)(?P<path>/.*)?$', views.event_proxy, name='event_proxy'),
]