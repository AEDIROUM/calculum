from django.urls import path
from . import views

urlpatterns = [
    path('', views.presentation, name='presentation'),
    path('noob', views.noob, name='noob'),
]
