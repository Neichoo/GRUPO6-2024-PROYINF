from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .models import Boletin, TagBoletin, TagFuente, Empleado, FuentesInfo, UsuarioLector, BoletinBorrador
from .forms import BusquedaBoletinForm, BusquedaFuenteForm
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from django.http import HttpResponseForbidden
from django.core.files import File
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import os
from weasyprint import HTML
from functools import wraps
from django.utils import timezone
import uuid

####
def equipou3i_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'Empleado') or request.user.Empleado.tipo != 'EquipoU3I':
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def bibliotecologo_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'Empleado') or request.user.Empleado.tipo != 'Bibliotecologo/a':
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
####

def Inicio(request):
    if request.user.is_authenticated:
        try:
            lector = request.user.usuariolector  # acceder correctamente al objeto relacionado
            tags, boletines, tagsSuscritos = dashboardLector(request)
            boletines_nuevos = lector.boletinesNuevos.all()
            if boletines_nuevos.exists():
                nombres = ', '.join([b.nombre_boletin for b in boletines_nuevos])
                messages.success(request, f"Tienes boletines nuevos: {nombres}", extra_tags='notificacion')
                lector.boletinesNuevos.clear()
            return render(request, "general/Inicio.html", {'temas': tags, 'boletines': boletines, 'tagsSuscritos': tagsSuscritos})
        except UsuarioLector.DoesNotExist:
            return render(request, "general/Inicio.html")
    return render(request, "general/Inicio.html")

def Sobre_vigifia(request):
    return render(request, "general/SobreVIGIFIA.html")

def Contacto(request):
    return render(request, "general/Contacto.html")

def Login_form(request):
    return render(request, "base/auth/Login.html")

def Register_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm = request.POST['confirm_password']
        email = request.POST['email']

        if password != confirm:
            messages.error(request, 'Las contraseñas no coinciden')
        elif User.objects.filter(username=username).exists():
           messages.error(request, 'El usuario ya existe')
        elif User.objects.filter(email__iexact=email).count() >= 1:
            messages.error(request, 'El correo ya está registrado')
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            UsuarioLector.objects.create(usuario=user)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirmation_link = f'http://localhost:8000/confirmar/{uid}/{token}/'

            subject = "Confirmación de Registro"
            html_message = render_to_string('base/auth/confirmation_email.html', {'confirmation_link': confirmation_link})
            plain_message = f'Gracias por registrarte en nuestra plataforma. Confirma tu cuenta aquí: {confirmation_link}'

            send_mail(
                subject,
                plain_message,
                'noreply@vigifia.com',
                [email],
                fail_silently=False,
                html_message=html_message
            )
            messages.success(request, 'Cuenta creada. Ahora inicia sesión.')
            return redirect('LoginUsuario')

    return render(request, 'base/auth/RegisterUsuario.html')

def confirm_registration(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            user.is_active = True 
            user.save()
            messages.success(request, 'Tu cuenta ha sido activada. Ahora puedes iniciar sesión.')
            return redirect('LoginUsuario')
        else:
            messages.error(request, 'El enlace de confirmación no es válido o ha expirado.')
            return redirect('Register_usuario')

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Enlace de confirmación inválido.')
        return redirect('Register_usuario')

def LoginUsuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, 'Por favor ingrese ambos campos: usuario y contraseña.')
            return render(request, 'base/auth/LoginUsuario.html')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('Inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'base/auth/LoginUsuario.html')

def Login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, 'Por favor ingrese ambos campos: usuario y contraseña.')
            return render(request, 'base/auth/Login.html')
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
                    return render(request, 'base/auth/Login.html')
            except Empleado.DoesNotExist:
                messages.error(request, 'Empleado no registrado en el sistema.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'base/auth/Login.html')

#Cerrar Sesión
@login_required(login_url='/Login/')
def Logout_view(request):
    logout(request)
    return redirect('Inicio')

#FUENTES Bilbiotecolog@s
@bibliotecologo_required
@login_required(login_url='/Login/')
def FuentesBiblio(request):
    form = BusquedaFuenteForm(request.GET or None)
    fuentes = FuentesInfo.objects.filter(estado='Activo')
    tags_conteo = TagFuente.objects.all()
    selected_tags = request.GET.getlist('filter') 
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            fuentes = fuentes.filter(Q(titulo__icontains=query))
        if selected_tags:
            for tag in selected_tags:
                fuentes = fuentes.filter(tags__nombre=tag)
    return render(request, 'bibliotecologos(as)/FuentesBiblio.html', {
        'form': form,
        'fuentes': fuentes,
        'tags_conteo': tags_conteo,
        'selected_tags': selected_tags,
    })


#FUENTES U3I
@login_required(login_url='/Login/')
@equipou3i_required
def FuentesU3I(request):
    form = BusquedaFuenteForm(request.GET or None)
    fuentes = FuentesInfo.objects.all()
    tags_conteo = TagFuente.objects.all()
    selected_tags = request.GET.getlist('filter')
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            fuentes = fuentes.filter(Q(titulo__icontains=query))
        if selected_tags:
            for tag in selected_tags:
                fuentes = fuentes.filter(tags__nombre=tag)

    return render(request, 'equipo_u3i/FuentesU3I.html', {
        'form': form,
        'fuentes': fuentes,
        'tags_conteo': tags_conteo,
        'selected_tags': selected_tags,
    })

@login_required(login_url='/Login/')
@equipou3i_required
def TagsFuentes(request):
    return render(request, "equipo_u3i/TagsFuentes.html")

@login_required(login_url='/Login/')
@bibliotecologo_required
def BoletinBiblio(request):
    return render(request, "bibliotecologos(as)/BoletinBiblio.html")

@login_required(login_url='/Login/')
@bibliotecologo_required
def subir_boletin_publicado(request):
    if request.method == "POST":
        nombre_boletin = request.POST['nombre_boletin']
        fecha_boletin = request.POST['fecha_boletin']
        tags_ids = request.POST.getlist('tags_boletin')  # Obtener los tags seleccionados
        url_pdf = request.FILES['url_pdf']  # Obtener el archivo PDF

        # Verificar si el boletín ya existe por nombre (opcional)
        try:
            boletin = Boletin.objects.get(nombre_boletin=nombre_boletin)
            messages.error(request, "Este boletín ya existe.")
        except Boletin.DoesNotExist:
            boletin = Boletin.objects.create(
                nombre_boletin=nombre_boletin,
                fecha_boletin=fecha_boletin,
                url_pdf=url_pdf
            )

            # Asignar los tags seleccionados
            for tag_id in tags_ids:
                tag = TagBoletin.objects.get(id=tag_id)
                boletin.tags_boletin.add(tag)

            boletin.save()  # Guardar la relación ManyToMany
            messages.success(request, "Boletín registrado exitosamente")

            #Mandar notificacion a todos los usuarios inscritos a la tag respectiva
            notificacionLector(boletin)

        return redirect('/SubirBoletin/')  # Redirigir después de crear el boletín

    # Obtener todos los tags disponibles para mostrarlos en el formulario
    tags_conteo = TagBoletin.objects.all()
    return render(request, 'bibliotecologos(as)/SubirBoletinPublicado.html', {
        'tags_conteo': tags_conteo
    })

@login_required(login_url='/Login/')
@bibliotecologo_required
def CrearBoletinBorrador(request):
    if request.method == 'POST':
        contenido_html = request.POST.get('basic-example', '')  # Asegura un string vacío si es None
        nombre_boletin = request.POST.get('nombre_boletin', 'Borrador sin título')

        if not contenido_html.strip():  # Valida que el contenido no esté vacío
            messages.error(request, 'El contenido del boletín no puede estar vacío.')
            return redirect('CrearBoletinBorrador')

        try:
            # Generar PDF
            pdf_filename = f"boletin_{uuid.uuid4().hex[:6]}.pdf"
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'PDF', pdf_filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            # Usa WeasyPrint con el contenido HTML
            HTML(string=contenido_html).write_pdf(pdf_path)

            # Guardar en la base de datos
            borrador = BoletinBorrador.objects.create(
                nombre_boletin=nombre_boletin,
                contenido_html=contenido_html,
                fecha_boletin=timezone.now().date(),
                url_pdf=f'PDF/{pdf_filename}'
            )

            messages.success(request, '¡Borrador y PDF guardados correctamente!')
            return redirect('AccesoBiblio')

        except Exception as e:
            messages.error(request, f'Error al generar el PDF: {str(e)}')
            return redirect('CrearBoletinBorrador')

    return render(request, 'bibliotecologos(as)/CrearBoletinBorrador.html')

@login_required(login_url='/Login/')
@bibliotecologo_required
def BoletinBorrador_listado(request):
    form = BusquedaBoletinForm(request.GET or None)
    boletines = BoletinBorrador.objects.all()
    tags_conteo = TagBoletin.objects.all()
    selected_tags = request.GET.getlist('filter')

    if form.is_valid():
        query = form.cleaned_data.get('query')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        ordenar_por = form.cleaned_data.get('ordenar_por')

        if query:
            boletines = boletines.filter(Q(nombre_boletin__icontains=query))
        
        if selected_tags:
            for tag in selected_tags:
                boletines = boletines.filter(tags_boletin__nombre=tag)

        if fecha_desde:
            boletines = boletines.filter(fecha_boletin__gte=fecha_desde)

        if fecha_hasta:
            boletines = boletines.filter(fecha_boletin__lte=fecha_hasta)

        if ordenar_por == 'asc':
            boletines = boletines.order_by('fecha_boletin')
        elif ordenar_por == 'desc':
            boletines = boletines.order_by('-fecha_boletin')

    return render(request, 'bibliotecologos(as)/EditarBoletinBorrador_listado.html', {
        'form': form,
        'boletines': boletines,
        'tags_conteo': tags_conteo,
        'selected_tags': selected_tags,
    })

@login_required(login_url='/Login/')
@bibliotecologo_required
def EditarBoletinBorrador(request, id_boletin):  
    boletin = get_object_or_404(BoletinBorrador, id_boletin=id_boletin)

    if request.method == 'POST':
        nuevo_contenido = request.POST.get('basic-example', '')
        nombre_boletin = request.POST.get('nombre_boletin', '').strip()

        # Validación de campos
        if not nombre_boletin:
            messages.error(request, 'El nombre del boletín no puede estar vacío.')
            return redirect('EditarBoletinBorrador', id_boletin=id_boletin)
            
        if not nuevo_contenido.strip():
            messages.error(request, 'El contenido del boletín no puede estar vacío.')
            return redirect('EditarBoletinBorrador', id_boletin=id_boletin)

        try:
            # Actualizar campos básicos
            boletin.nombre_boletin = nombre_boletin
            boletin.contenido_html = nuevo_contenido
            boletin.fecha_boletin = timezone.now().date()

            # Generar nuevo PDF
            pdf_filename = f"boletin_{uuid.uuid4().hex[:6]}.pdf"
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'PDF', pdf_filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            HTML(string=nuevo_contenido).write_pdf(pdf_path)

            # Actualizar archivo PDF
            with open(pdf_path, 'rb') as pdf_file:
                django_file = File(pdf_file)
                boletin.url_pdf.save(pdf_filename, django_file, save=False)

            # Guardar todos los cambios
            boletin.save()

            messages.success(request, '¡Boletín actualizado correctamente!')
            return redirect('AccesoBiblio')

        except Exception as e:
            messages.error(request, f'Error al actualizar el boletín: {str(e)}')
            return redirect('EditarBoletinBorrador', id_boletin=id_boletin)

    return render(request, 'bibliotecologos(as)/EditarBoletinBorrador_editar.html', {
        'boletin': boletin
    })

@login_required(login_url='/Login/')
@bibliotecologo_required
def BorrarBoletin(request):
    boletines = Boletin.objects.all()
    return render(request, 'bibliotecologos(as)/BorrarBoletin.html', {'boletines' : boletines})

@login_required(login_url='/Login/')
@bibliotecologo_required
def BorradoBoletin(request, id_boletin):
    boletin = Boletin.objects.get(id_boletin = id_boletin)
    boletin.delete()
    return redirect('/BorrarBoletin/')

#Ingreso fuentes
@login_required(login_url='/Login/')
@equipou3i_required
def IngresarFuente(request):
    tags_conteo = TagFuente.objects.all()
    return render(request, 'equipo_u3i/IngresarFuente.html', {
        'tags_conteo': tags_conteo
    })

@login_required(login_url='/Login/')
@equipou3i_required
def IngresoFuente(request):
    if request.method == "POST":
        titulo = request.POST['titulo']
        url = request.POST['url']
        estado = request.POST['estado']
        descripcion = request.POST['descripcion']
        tags_ids = request.POST.getlist('tags')
        try:
            fuente = FuentesInfo.objects.get(url=url)
            existeFuente = True
        except FuentesInfo.DoesNotExist:
            existeFuente = False
        if not existeFuente:
            fuente = FuentesInfo.objects.create(
                titulo=titulo,
                url=url,
                estado=estado,
                descripcion=descripcion,
            )
            for tag_id in tags_ids:
                tag = TagFuente.objects.get(id=tag_id)
                fuente.tags.add(tag)
            fuente.save()
            messages.success(request, "Fuente registrada exitosamente")
        else:
            messages.error(request, "Ya existe esta URL dentro de la base de datos")
        return redirect('/IngresarFuente/')
    return redirect('/IngresarFuente/')

@login_required(login_url='/Login/')
@equipou3i_required
def IngresarTagFuente(request):
    return render(request, "equipo_u3i/IngresarTagFuente.html")

def IngresoTagFuente(request):
    nombre = request.POST['nombre']

    try:
        tag = TagFuente.objects.get(nombre = nombre)
        existeTag = True
    except TagFuente.DoesNotExist:
        existeTag = False

    if existeTag == False:
        messages.success(request, "Tag registrada exitosamente")
        tag = TagFuente.objects.create(
            nombre = nombre,
        )
    else:
        messages.error(request, "Ya existe esta tag dentro de la base de datos")
    
    return redirect('/IngresarTagFuente/')

@login_required(login_url='/Login/')
@equipou3i_required
def BorrarTagFuente(request):
    if not hasattr(request.user, 'Empleado') or request.user.Empleado.tipo != 'EquipoU3I':
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    tags = TagFuente.objects.all()
    return render(request, "equipo_u3i/BorrarTagFuente.html",  {"tags": tags})

@login_required(login_url='/Login/')
@equipou3i_required
def BorradoTagFuente(request, nombre):
    tag = TagFuente.objects.get(nombre = nombre)
    tag.delete()
    return redirect("/BorrarTagFuente/")


#Modificar fuentes
@login_required(login_url='/Login/')
@equipou3i_required
def ModificarFuente(request, id_fuente):
    fuente = FuentesInfo.objects.get(id_fuente = id_fuente)
    return render(request, "equipo_u3i/ModificarFuente.html", {"fuente": fuente})

@login_required(login_url='/Login/')
@equipou3i_required
def EditarFuente(request, id_fuente):
    titulo = request.POST['titulo']
    url = request.POST['url']
    #tags = request.POST['tags']
    estado = request.POST['estado']
    descripcion = request.POST['descripcion']

    try:
        fuente = FuentesInfo.objects.get(url = url)
        existeFuente = True
    except FuentesInfo.DoesNotExist:
        existeFuente = False

    if existeFuente == True:
        fuente.titulo = titulo
        fuente.url = url
        #fuente.tags = tags
        fuente.estado = estado
        fuente.descripcion = descripcion

        fuente.save()
        messages.success(request, "Fuente ingresada exitosamente")
    else:
        messages.error(request, "Ya existe una fuente con esta url")

    return redirect('/ModificarFuente/' + str(id_fuente) + '/')

#Acceso Bilbiotecolog@s
@bibliotecologo_required
@login_required(login_url='/Login/')
def AccesoBiblio(request):
    return render(request, "bibliotecologos(as)/AccesoBiblio.html")

@login_required(login_url='/Login/')
@equipou3i_required
def Estadisticas(request):
    return render(request, "equipo_u3i/Estadisticas.html")

@login_required(login_url='/Login/')
@equipou3i_required
def PanelDeControl(request):
    return render(request, "equipo_u3i/PanelDeControl.html")

def Boletines(request):
    form = BusquedaBoletinForm(request.GET or None)
    boletines = Boletin.objects.all()
    tags_conteo = TagBoletin.objects.all()
    selected_tags = request.GET.getlist('filter')
    if form.is_valid():
        query = form.cleaned_data.get('query')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        ordenar_por = form.cleaned_data.get('ordenar_por')
        if query:
            boletines = boletines.filter(Q(nombre_boletin__icontains=query))
        if selected_tags:
            for tag in selected_tags:
                boletines = boletines.filter(tags_boletin__nombre=tag)
        if fecha_desde:
            boletines = boletines.filter(fecha_boletin__gte=fecha_desde)
        if fecha_hasta:
            boletines = boletines.filter(fecha_boletin__lte=fecha_hasta)
        if ordenar_por == 'asc':
            boletines = boletines.order_by('fecha_boletin')
        elif ordenar_por == 'desc':
            boletines = boletines.order_by('-fecha_boletin')

    return render(request, 'general/boletines.html', {
        'form': form,
        'boletines': boletines,
        'tags_conteo': tags_conteo,
        'selected_tags': selected_tags,
    })

def dashboardLector(request):
    #Agregar tags si el usuario esta logueado
    tags = TagBoletin.objects.all()
    tagsSuscritos = request.user.usuariolector.preferenciasTags.all()

    hace_7_dias = timezone.now().date() - timedelta(days=7)

    boletines = Boletin.objects.filter(
        tags_boletin__in=tagsSuscritos,
        fecha_boletin__gte=hace_7_dias
    ).distinct()

    return (tags, boletines, tagsSuscritos)

def suscribirTema(request, nombreTema):
    if request.user.is_authenticated and hasattr(request.user, 'usuariolector'):
        tema = TagBoletin.objects.get(nombre=nombreTema)
        request.user.usuariolector.preferenciasTags.add(tema)
        messages.success(request, f"Te has suscrito al tema '{tema.nombre}' exitosamente.", extra_tags='suscripcion')
    return redirect('Inicio')

def desuscribirTema(request, nombreTema):
    if request.user.is_authenticated and hasattr(request.user, 'usuariolector'):
        tema = TagBoletin.objects.get(nombre=nombreTema)
        request.user.usuariolector.preferenciasTags.remove(tema)
        messages.success(request, f"Te has desuscrito del tema '{tema.nombre}' exitosamente.", extra_tags='suscripcion')
    return redirect('Inicio')

def notificacionLector(boletin):
    lectores = UsuarioLector.objects.filter(preferenciasTags__in=boletin.tags_boletin.all()).distinct()
    for lector in lectores:
        lector.boletinesNuevos.add(boletin)
