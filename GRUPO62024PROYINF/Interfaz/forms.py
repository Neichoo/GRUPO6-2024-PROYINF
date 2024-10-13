from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Tag

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class BusquedaBoletinForm(forms.Form):
    palabras_clave = forms.CharField(max_length=100, required=False, label='Buscar boletines')
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False
    )
    fecha_inicio = forms.DateField(required=False, widget=forms.SelectDateWidget, label='Desde')
    fecha_fin = forms.DateField(required=False, widget=forms.SelectDateWidget, label='Hasta')
    ordenar_por_fecha = forms.ChoiceField(
        choices=[('asc', 'Fecha Ascendente'), ('desc', 'Fecha Descendente')],
        required=False,
        label='Ordenar por fecha'
    )
    operador_logico = forms.ChoiceField(
        choices=[('and', 'Y'), ('or', 'O')],
        required=True,
        label='Operador lógico'
    )