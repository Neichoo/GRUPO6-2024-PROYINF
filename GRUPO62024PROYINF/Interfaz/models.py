from django.db import models

# Create your models here.

class Tag(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nombre
    
class Boletin(models.Model):
    id_boletin = models.AutoField(primary_key=True)
    nombre_boletin = models.CharField(max_length=100)
    tags_boletin = models.ManyToManyField(Tag)
    fecha_boletin = models.DateField()
    def __str__(self):
        return self.nombre_boletin


