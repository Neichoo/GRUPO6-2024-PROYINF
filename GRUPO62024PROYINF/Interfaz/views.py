from django.shortcuts import render

# Create your views here.

def inicio(request):
    return render(request, "Inicio.html")
def boletines(request):
    return render(request, "Boletines.html")
def sobre_vigifia(request):
    return render(request, "SobreVIGIFIA.html")
def contacto(request):
    return render(request, "Contacto.html")
def login(request):
    return render(request, "Login.html")