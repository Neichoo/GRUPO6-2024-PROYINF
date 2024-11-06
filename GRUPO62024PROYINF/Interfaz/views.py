from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Boletin, Tag, Empleado, FuentesInfo
from .forms import BusquedaBoletinForm
from django.db.models import Q


def Inicio(request):
    return render(request, "Inicio.html")

def Sobre_vigifia(request):
    return render(request, "SobreVIGIFIA.html")

def Contacto(request):
    return render(request, "Contacto.html")

def Login_form(request):
    return render(request, "Login.html")

def Login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, 'Por favor ingrese ambos campos: usuario y contraseña.')
            return render(request, 'Login.html')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            try:
                empleado = Empleado.objects.get(usuario=user)
                if empleado.tipo == Empleado.EQUIPO_U3I:
                    return redirect('PanelDeControl')
                elif empleado.tipo == Empleado.BIBLIOTECOLOGO:
                    return redirect('AccesoBiblio')
                else:
                    messages.error(request, 'Tipo de empleado no reconocido.')
                    return render(request, 'Login.html')
            except Empleado.DoesNotExist:
                messages.error(request, 'Empleado no registrado en el sistema.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'Login.html')

#FUENTES
@login_required(login_url='/Login/')
def Fuentes(request):
    return render(request, "Fuentes.html")

#Acceso Bilbiotecolog@s
@login_required(login_url='/Login/')
def AccesoBiblio(request):
    return render(request, "AccesoBiblio.html")

@login_required(login_url='/Login/')
def Estadisticas(request):
    return render(request, "Estadisticas.html")

@login_required(login_url='/Login/')
def PanelDeControl(request):
    return render(request, "PanelDeControl.html")

def Logout_view(request):
    logout(request)
    return redirect('Login')

def Boletines(request):
    form = BusquedaBoletinForm(request.GET or None)
    boletines = Boletin.objects.all()
    tags_conteo = Tag.objects.all()
    if form.is_valid():
        query = form.cleaned_data.get('query')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        ordenar_por = form.cleaned_data.get('ordenar_por')
        # Filtrar por palabras clave en nombre del boletín
        if query:
            boletines = boletines.filter(
                Q(nombre_boletin__icontains=query)
            )
        # Filtrar por tag seleccionado en el menú desplegable
        tag_filter = request.GET.get('filter')
        if tag_filter:
            boletines = boletines.filter(tags_boletin__nombre=tag_filter)
        # Filtrar por rango de fechas
        if fecha_desde:
            boletines = boletines.filter(fecha_boletin__gte=fecha_desde)
        if fecha_hasta:
            boletines = boletines.filter(fecha_boletin__lte=fecha_hasta)
        # Ordenar por fecha
        if ordenar_por == 'asc':
            boletines = boletines.order_by('fecha_boletin')
        elif ordenar_por == 'desc':
            boletines = boletines.order_by('-fecha_boletin')

    return render(request, 'boletines.html', {
        'form': form,
        'boletines': boletines,
        'tags_conteo': tags_conteo
    })