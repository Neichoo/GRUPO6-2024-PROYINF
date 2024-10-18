from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
     path('', RedirectView.as_view(url='Inicio/', permanent=False)),
    path('Inicio/', views.Inicio, name='Inicio'),
    path('Boletines/', views.Boletines, name='Boletines'),
    path('SobreVIGIFIA/', views.Sobre_vigifia, name='Sobre_vigifia'),
    path('Contacto/', views.Contacto, name='Contacto'),
    path('Login/', views.Login_form, name='Login'), 
    path('Login_view/', views.Login_view, name='Login_view'),
    path('PanelDeControl/', views.PanelDeControl, name='PanelDeControl'),
    path('logout/', views.Logout_view, name='logout'),
    path('Fuentes/', views.Fuentes, name='Fuentes'),
    path('Estadisticas/', views.Estadisticas, name='Estadisticas'),
    path('AccesoBiblio/', views.AccesoBiblio, name='AccesoBiblio'),
    
]