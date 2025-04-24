from django.db import models
from django.contrib.auth.models import User



class TagBoletin(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nombre

class TagFuente(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nombre

class FuentesInfo(models.Model):
    ACTIVO = 'Activo'
    DESACTIVADO = 'Desactivado'
    ESTADO_CHOICES = [
        (ACTIVO, 'Activo'),
        (DESACTIVADO, 'Desactivado'),
    ]

    id_fuente = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100, default="")
    url = models.CharField(max_length=100, unique=True)
    tags = models.ManyToManyField(TagFuente)
    estado = models.CharField(
        max_length=12,
        choices=ESTADO_CHOICES,
        default=ACTIVO,
    )
    descripcion = models.CharField(max_length=500, default="", blank=True, null=True)
    def __str__(self):
        return self.url

class Boletin(models.Model):
    id_boletin = models.AutoField(primary_key=True)
    nombre_boletin = models.CharField(max_length=100)
    tags_boletin = models.ManyToManyField(TagBoletin)
    fecha_boletin = models.DateField()
    url_pdf = models.FileField(upload_to='PDF/')
    
    def __str__(self):
        return self.nombre_boletin

class Empleado(models.Model):
    EQUIPO_U3I = 'EquipoU3I'
    BIBLIOTECOLOGO = 'Bibliotecologo/a'
    
    TIPO_CHOICES = [
        (EQUIPO_U3I, 'EquipoU3I'),
        (BIBLIOTECOLOGO, 'Bibliotecologo/a'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)

class UsuarioLector(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    #placeholder
    preferencias = models.CharField(max_length=50, default='')
    notificaciones = models.BooleanField(default=True)


def get_empleado(self):
    try:
        return self.empleado
    except self.empleado.DoesNotExist:
        return None
       
def get_usuariolector(self):
    try:
        return self.usuariolector
    except self.usuariolector.DoesNotExist:
        return None
    
User.add_to_class("Empleado", property(get_empleado))
User.add_to_class("UsuarioLector", property(get_usuariolector))