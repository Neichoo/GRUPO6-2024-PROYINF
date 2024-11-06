from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class BusquedaBoletinForm(forms.Form):
    query = forms.CharField(
        required=False, 
        label="Buscar", 
        widget=forms.TextInput(attrs={'placeholder': 'Buscar boletines...'})
    )
    fecha_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Desde")
    fecha_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Hasta")
    ordenar_por = forms.ChoiceField(
        choices=[('asc', 'Fecha Ascendente'), ('desc', 'Fecha Descendente')],
        required=False,
        label="Ordenar por fecha"
    )

class BusquedaFuenteForm(forms.Form):
    query = forms.CharField(
        required=False, 
        label="Buscar", 
        widget=forms.TextInput(attrs={'placeholder': 'Buscar fuentes...'})
    )