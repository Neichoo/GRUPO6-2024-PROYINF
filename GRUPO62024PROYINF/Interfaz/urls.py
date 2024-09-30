from django.urls import path
from . import views

urlpatterns = [
    path('Inicio/', views.inicio),
    path('Boletines/', views.boletines),
    path('SobreVIGIFIA/', views.sobre_vigifia),
    path('Contacto/', views.contacto),
    path('Login/', views.login),
]