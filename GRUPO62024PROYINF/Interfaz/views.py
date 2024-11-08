from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Boletin, Tag, Empleado, FuentesInfo
from .forms import BusquedaBoletinForm, BusquedaFuenteForm
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

#FUENTES Bilbiotecolog@s
@login_required(login_url='/Login/')
def FuentesBiblio(request):
    form = BusquedaFuenteForm(request.GET or None)
    fuentes = FuentesInfo.objects.filter(estado='Activo')
    tags_conteo = Tag.objects.all()
    if form.is_valid():
        query = form.cleaned_data.get('query')
        # Filtrar por palabras clave en nombre del boletín
        if query:
            fuentes = fuentes.filter(
                Q(titulo__icontains=query)
            )
        # Filtrar por tag seleccionado en el menú desplegable
        tag_filter = request.GET.get('filter')
        if tag_filter:
            fuentes = fuentes.filter(tags__nombre=tag_filter)

    return render(request, 'FuentesBiblio.html', {
        'form': form,
        'fuentes': fuentes,
        'tags_conteo': tags_conteo
    })

#FUENTES U3I
@login_required(login_url='/Login/')
def FuentesU3I(request):
    form = BusquedaFuenteForm(request.GET or None)
    fuentes = FuentesInfo.objects.filter(estado='Activo')
    tags_conteo = Tag.objects.all()
    if form.is_valid():
        query = form.cleaned_data.get('query')
        # Filtrar por palabras clave en nombre del boletín
        if query:
            fuentes = fuentes.filter(
                Q(titulo__icontains=query)
            )
        # Filtrar por tag seleccionado en el menú desplegable
        tag_filter = request.GET.get('filter')
        if tag_filter:
            fuentes = fuentes.filter(tags__nombre=tag_filter)

    return render(request, 'FuentesU3I.html', {
        'form': form,
        'fuentes': fuentes,
        'tags_conteo': tags_conteo
    })

#Ingreso fuentes
@login_required(login_url='/Login/')
def IngresarFuente(request):
    return render(request, "IngresarFuente.html")

def IngresoFuente(request):
    titulo = request.POST['titulo']
    url = request.POST['url']
    #tags = request.POST['tags']
    estado = request.POST['estado']
    descripcion = request.POST['descripcion']
    fuente = FuentesInfo.objects.create(
        titulo = titulo,
        url = url,
        estado = estado,
        descripcion = descripcion,
    )

    return redirect('/IngresarFuente/')

#Modificar fuentes
@login_required(login_url='/Login/')
def ModificarFuente(request, id_fuente):
    fuente = FuentesInfo.objects.get(id_fuente = id_fuente)
    return render(request, "ModificarFuente.html", {"fuente": fuente})

@login_required(login_url='/Login/')
def EditarFuente(request, id_fuente):
    titulo = request.POST['titulo']
    url = request.POST['url']
    #tags = request.POST['tags']
    estado = request.POST['estado']
    descripcion = request.POST['descripcion']

    fuente = FuentesInfo.objects.get(id_fuente=id_fuente)

    fuente.titulo = titulo
    fuente.url = url
    #fuente.tags = tags
    fuente.estado = estado
    fuente.descripcion = descripcion

    fuente.save()

    return redirect('/FuentesU3I/')

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

    # Aplicar filtros si el formulario es válido
    if form.is_valid():
        query = form.cleaned_data.get('query')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        ordenar_por = form.cleaned_data.get('ordenar_por')
        tag_filter = form.cleaned_data.get('filter')  # Si 'filter' es un campo en el formulario

        # Filtrar por palabras clave en el nombre del boletín
        if query:
            boletines = boletines.filter(Q(nombre_boletin__icontains=query))
        
        # Filtrar por tag seleccionado si está presente
        if tag_filter:
            boletines = boletines.filter(tags_boletin__nombre=tag_filter)
        
        # Filtrar por rango de fechas si están definidos
        if fecha_desde:
            boletines = boletines.filter(fecha_boletin__gte=fecha_desde)
        if fecha_hasta:
            boletines = boletines.filter(fecha_boletin__lte=fecha_hasta)
        
        # Ordenar resultados por fecha
        if ordenar_por == 'asc':
            boletines = boletines.order_by('fecha_boletin')
        elif ordenar_por == 'desc':
            boletines = boletines.order_by('-fecha_boletin')

    return render(request, 'boletines.html', {
        'form': form,
        'boletines': boletines,
        'tags_conteo': tags_conteo
    })