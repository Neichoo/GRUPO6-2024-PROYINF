from django.contrib import admin
from .models import Tag, Boletin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Empleado

class EmpleadoInLine(admin.StackedInline):
    model = Empleado
    can_delete = False
    verbose_name_plural = "Empleado"

class UsuarioAdmin(BaseUserAdmin):
    inlines = [EmpleadoInLine]

admin.site.register(Tag)
admin.site.register(Boletin)
admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)