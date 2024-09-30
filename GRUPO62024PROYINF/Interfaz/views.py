from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm

def Inicio(request):
    return render(request, "Inicio.html")
def Boletines(request):
    return render(request, "Boletines.html")
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
            return redirect('PanelDeControl')  # Redirige a la página principal o donde desees
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'Login.html')
@login_required(login_url='/Login/')
def PanelDeControl(request):
    return render(request, "PanelDeControl.html")
