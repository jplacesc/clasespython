from django.contrib import admin

# -*- coding: latin-1 -*-
from django.contrib import admin
from django.contrib.admin.models import LogEntry
# from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.models import Permission

from app.models import *


class ModeloBaseTabularAdmin(admin.TabularInline):
    exclude = ("usuario_creacion", "fecha_creacion", "usuario_modificacion", "fecha_modificacion")


class ModeloBaseAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        actions = super(ModeloBaseAdmin, self).get_actions(request)
        return actions

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("usuario_creacion", "fecha_creacion", "usuario_modificacion", "fecha_modificacion")
        form = super(ModeloBaseAdmin, self).get_form(request, obj, **kwargs)
        return form

class ClienteAdmin(ModeloBaseAdmin):
    list_display = ('nombre', 'apellido', 'sexo', 'email', 'celular', 'provincia', 'usuario')
    ordering = ('nombre','apellido',)
    search_fields = ('nombre', 'apellido', 'identificacion')
    list_filter = ('provincia', 'sexo')

class ModuloAdmin(ModeloBaseAdmin):
    list_display = ('url', 'nombre', 'icono', 'descripcion', )
    ordering = ('nombre',)
    search_fields = ('url', 'nombre', 'descripcion')
    list_filter = ('nombre', 'descripcion')

class OpcionModuloAdmin(ModeloBaseAdmin):
    list_display = ('url', 'nombre', 'orden', 'descripcion',)
    ordering = ('nombre',)
    search_fields = ('url', 'nombre', 'descripcion')
    list_filter = ('nombre', 'modulo')


class SucursalAdmin(ModeloBaseAdmin):
    list_display = ('nombre_comercial', 'direccion', 'email','actividad_economica',)
    ordering = ('nombre_comercial',)
    search_fields = ('nombre_comercial', 'actividad_economica',)
    list_filter = ('nombre_comercial',)


class PaisAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)
    list_filter = ('nombre',)


class ProvinciaAdmin(ModeloBaseAdmin):
    list_display = ('nombre','pais',)
    ordering = ('nombre',)
    search_fields = ('nombre',)
    list_filter = ('nombre',)


class CiudadAdmin(ModeloBaseAdmin):
    list_display = ('nombre','provincia',)
    ordering = ('nombre','provincia',)
    search_fields = ('nombre',)
    list_filter = ('nombre',)

class VendedorAdmin(ModeloBaseAdmin):
    list_display = ('identificacion','nombre','apellido',)
    ordering = ('identificacion','nombre','apellido',)
    search_fields = ('identificacion','nombre','apellido',)
    list_filter = ('identificacion','nombre','apellido',)

class ModuloGrupoAdmin(ModeloBaseAdmin):
    list_display = ('nombre', 'prioridad', 'descripcion')
    ordering = ('prioridad', 'nombre')
    search_fields = ('nombre', 'descripcion')

class LogEntryAdmin(ModeloBaseAdmin):
    date_hierarchy = 'action_time'
    list_filter = ['action_flag']
    search_fields = ['change_message', 'object_repr', 'user__username']
    list_display = ['action_time', 'user', 'action_flag', 'change_message']

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        self.readonly_fields = [x.name for x in self.model._meta.local_fields]
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
         raise Exception('Sin permiso a modificacion')

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Modulo, ModuloAdmin)
admin.site.register(OpcionModulo, OpcionModuloAdmin)
admin.site.register(Sucursal, SucursalAdmin)
admin.site.register(Pais, PaisAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Ciudad, CiudadAdmin)
admin.site.register(Vendedor, VendedorAdmin)
admin.site.register(ModuloGrupo, ModuloGrupoAdmin)
admin.site.register(Permission, ModeloBaseAdmin)
admin.site.register(LogEntry, LogEntryAdmin)