from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Boletin, Tag, Empleado, FuentesInfo
from .forms import BusquedaBoletinForm
from django.db.models import Q, Count

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
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                # Obtener el tipo del empleado
                empleado = Empleado.objects.get(usuario=user)
                if empleado.tipo == Empleado.EQUIPO_U3I:
                    return redirect('PanelDeControl')  # Redirige al template del Equipo U3I
                elif empleado.tipo == Empleado.BIBLIOTECOLOGO:
                    return redirect('Contacto')  # Redirige al template del Bibliotecólogo/a
            except Empleado.DoesNotExist:
                messages.error(request, 'Empleado no registrado.')

        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'Login.html')

#FUENTES
@login_required(login_url='/Login/')
def Fuentes(request):
    fuentes = FuentesInfo.objects.all()
    
    if request.method == 'POST':
        if 'agregar_fuente' in request.POST:
            url = request.POST.get('url')
            nueva_fuente = FuentesInfo(url=url)
            nueva_fuente.save()
            return redirect('Fuentes')
        
        elif 'editar_fuente' in request.POST: 
            id_fuente = request.POST.get('id_fuente')
            fuente = get_object_or_404(FuentesInfo, id_fuente=id_fuente)
            fuente.url = request.POST.get('url')
            fuente.save()
            return redirect('Fuentes')
        
        elif 'eliminar_fuente' in request.POST:
            id_fuente = request.POST.get('id_fuente')
            fuente = get_object_or_404(FuentesInfo, id_fuente=id_fuente)
            fuente.delete()
            return redirect('Fuentes')

    return render(request, 'Fuentes.html', {'fuentes': fuentes})

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
    tags_conteo = Tag.objects.annotate(num_boletines=Count('boletin')).order_by('-num_boletines')
    
    if form.is_valid():
        palabras_clave = form.cleaned_data.get('palabras_clave')
        selected_tag = request.GET.get('filter')
        fecha_inicio = form.cleaned_data.get('fecha_inicio')
        fecha_fin = form.cleaned_data.get('fecha_fin')
        ordenar_por_fecha = form.cleaned_data.get('ordenar_por_fecha')
        operador_logico = form.cleaned_data.get('operador_logico')
        # Filtrar por palabras clave en el título o contenido
        if palabras_clave:
            boletines = boletines.filter(Q(nombre_boletin__icontains=palabras_clave))
        # Filtrar por tag seleccionado
        if selected_tag:
            boletines = boletines.filter(tags_boletin__nombre=selected_tag)  # Filtrar por el tag seleccionado
        # Filtrar por rango de fechas
        if fecha_inicio:
            boletines = boletines.filter(fecha_boletin__gte=fecha_inicio)
        if fecha_fin:
            boletines = boletines.filter(fecha_boletin__lte=fecha_fin)
        # Ordenar por fecha
        if ordenar_por_fecha == 'asc':
            boletines = boletines.order_by('fecha_boletin')
        elif ordenar_por_fecha == 'desc':
            boletines = boletines.order_by('-fecha_boletin')
    context = {
        'form': form,
        'boletines': boletines,
        'tags_conteo': tags_conteo 
    }
    return render(request, 'Boletines.html', context)