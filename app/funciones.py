# coding=utf-8
from __future__ import division

import re
import sys
from datetime import timedelta, date, time
from operator import itemgetter
import os
import json
import io as StringIO

from django.db import models, connection, connections
from django.contrib.admin.models import LogEntry, ADDITION, DELETION, CHANGE
from django.contrib.auth.models import User, Group, _user_has_perm
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Func, Q, Avg, F,Count

import unicodedata
import socket
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime


unicode = str


class MiPaginador(Paginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, rango=5):
        super(MiPaginador, self).__init__(object_list, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)
        self.rango = rango
        self.paginas = []
        self.primera_pagina = False
        self.ultima_pagina = False

    def rangos_paginado(self, pagina):
        left = pagina - self.rango
        right = pagina + self.rango
        if left < 1:
            left = 1
        if right > self.num_pages:
            right = self.num_pages
        self.paginas = range(left, right + 1)
        self.primera_pagina = True if left > 1 else False
        self.ultima_pagina = True if right < self.num_pages else False
        self.ellipsis_izquierda = left - 1
        self.ellipsis_derecha = right + 1



def log(mensaje, request, accion, user=None):

    if accion == "del":
        logaction = DELETION
    elif accion == "add":
        logaction = ADDITION
    else:
        logaction = CHANGE

    LogEntry.objects.log_action(
        user_id=request.user.id if not user else user.id,
        content_type_id=None,
        object_id=None,
        object_repr='',
        action_flag=logaction,
        change_message=unicode(mensaje))


def convertir_fecha(s):
    if ':' in s:
        sep = ':'
    elif '-' in s:
        sep = '-'
    else:
        sep = '/'

    return date(int(s.split(sep)[2]), int(s.split(sep)[1]), int(s.split(sep)[0]))


def convertir_hora(s):
    if ':' in s:
        sep = ':'
    return time(int(s.split(sep)[0]), int(s.split(sep)[1]))


def convertir_hora_completa(s):
    if ':' in s:
        sep = ':'
    return time(int(s.split(sep)[0]), int(s.split(sep)[1]), int(s.split(sep)[2]))


def convertir_fecha_invertida(s):
    if ':' in s:
        sep = ':'
    elif '-' in s:
        sep = '-'
    else:
        sep = '/'
    return date(int(s.split(sep)[0]), int(s.split(sep)[1]), int(s.split(sep)[2]))

def convertir_fecha_invertida_hora(s):
    if ':' in s:
        sep = ':'
    elif '-' in s:
        sep = '-'
    else:
        sep = '/'
    return datetime(int(s.split(sep)[0]), int(s.split(sep)[1]), int(s.split(sep)[2]), int(s.split(sep)[3]),
                    int(s.split(sep)[4]))


def convertir_fecha_hora(s):
    fecha = s.split(' ')[0]
    hora = s.split(' ')[1]
    if '/' in fecha:
        sep = ':'
    elif '-' in fecha:
        sep = '-'
    else:
        sep = ':'
    return datetime(int(fecha.split(sep)[2]), int(fecha.split(sep)[1]), int(fecha.split(sep)[0]),
                    int(hora.split(':')[0]), int(hora.split(':')[1]))


def convertir_fecha_hora_invertida(s):
    fecha = s.split(' ')[0]
    hora = s.split(' ')[1]
    if '/' in fecha:
        sep = ':'
    elif '-' in fecha:
        sep = '-'
    else:
        sep = ':'
    return datetime(int(fecha.split(sep)[0]), int(fecha.split(sep)[1]), int(fecha.split(sep)[2]),
                    int(hora.split(':')[0]), int(hora.split(':')[1]))

def round_half_up(n, decimals=0):
    import math
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

class ModeloBase(models.Model):
    """ Modelo base para todos los modelos del proyecto """
    from django.contrib.auth.models import User
    status = models.BooleanField(default=True)
    usuario_creacion = models.ForeignKey(User, related_name='+', blank=True, null=True, on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    usuario_modificacion = models.ForeignKey(User, related_name='+', blank=True, null=True, on_delete=models.SET_NULL)
    fecha_modificacion = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        usuario = None
        fecha_modificacion = datetime.now()
        fecha_creacion = None
        if len(args):
            usuario = args[0].user.id
        for key, value in kwargs.items():
            if 'usuario_id' == key:
                usuario = value
            if 'fecha_modificacion' == key:
                fecha_modificacion = value
            if 'fecha_creacion' == key:
                fecha_creacion = value
        if self.id:
            self.usuario_modificacion_id = usuario if usuario else 1
            self.fecha_modificacion = fecha_modificacion
        else:
            self.usuario_creacion_id = usuario if usuario else 1
            self.fecha_creacion = fecha_modificacion
            if fecha_creacion:
                self.fecha_creacion = fecha_creacion
        models.Model.save(self)

    class Meta:
        abstract = True

def cargar_plantilla_base_simple(request, data):
    from app.models import Modulo, Sucursal, OpcionModulo, ModuloGrupo
    data['usuario'] = usuario = request.session['usuario']
    modulos = Modulo.objects.filter(status=True, activo=True)
    data['modulos'] = modulos
    data['sucursalsesion'] = request.session['sucursalsesion']
    if usuario.is_superuser:
        if Sucursal.objects.values('id').filter(status=True,tipo=2).exists():
            sucursales = Sucursal.objects.filter(status=True,tipo=2)
    elif 'vendedor' in request.session:
        vendedor = request.session['vendedor']
        if vendedor.obtener_sucursal():
            if Sucursal.objects.values('id').filter(id=vendedor.obtener_sucursal().sucursal_id).exists() and not usuario.is_superuser:
                sucursales = Sucursal.objects.filter(id=vendedor.obtener_sucursal().sucursal_id)
    data['sucursales'] = sucursales
def carga_plantilla_base(request, data):
    from app.models import Modulo,Sucursal,OpcionModulo,ModuloGrupo
    data['currenttime'] = datetime.now()
    data['usuario'] =usuario= request.session['usuario']
    sucursales = None
    modulos = None
    opciones = None
    data['sucursalsesion']=request.session['sucursalsesion']
    if usuario.is_superuser:
        if Sucursal.objects.values('id').filter(status=True).exists():
            sucursales = Sucursal.objects.filter(status=True)
        modulos = Modulo.objects.filter(status=True, activo=True)

    elif 'vendedor' in request.session:
        vendedor = request.session['vendedor']
        if vendedor.obtener_sucursal():
            if Sucursal.objects.values('id').filter(id=vendedor.obtener_sucursal().sucursal_id).exists() and not usuario.is_superuser:
                sucursales = Sucursal.objects.filter(id=vendedor.obtener_sucursal().sucursal_id)
        idmodulos = ModuloGrupo.objects.values_list('opcion__modulo', flat=True).filter(grupos__in=usuario.groups.all(),status=True).distinct()
        opciones = ModuloGrupo.objects.values_list('opcion__id', flat=True).filter(grupos__in=usuario.groups.all(),status=True).distinct()
        modulos = Modulo.objects.filter(status=True, id__in=idmodulos, activo=True)
    data['sucursales'] = sucursales
    data['modulos'] = modulos
    data['misopciones'] = opciones
    if 'ruta' not in request.session:
        request.session['ruta'] = [['/', 'Inicio']]
    rutalista = request.session['ruta']
    if request.path:
        if OpcionModulo.objects.filter(url=request.path[1:]).exists():
            modulo = OpcionModulo.objects.filter(url=request.path[1:])[0]
            url = ['/' + modulo.url, modulo.nombre]
            if rutalista.count(url) <= 0:
                if rutalista.__len__() >= 3:
                    b = rutalista[1]
                    rutalista.remove(b)
                    rutalista.append(url)
                else:
                    rutalista.append(url)
            request.session['ruta'] = rutalista
            data["url_back"] = '/'
            url_back = [data['url_back']]
            request.session['url_back'] = url_back
    data["ruta"] = rutalista

def calculate_username(persona, variant=1):
    alfabeto = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
                'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    s = persona.nombres.lower().split(' ')
    while '' in s:
        s.remove('')
    if persona.apellido2:
        usernamevariant = s[0][0] + persona.apellido1.lower() + persona.apellido2.lower()[0]
    else:
        usernamevariant = s[0][0] + persona.apellido1.lower()
    usernamevariant = usernamevariant.replace(' ', '').replace(u'ñ', 'n').replace(u'á', 'a').replace(u'é', 'e').replace(
        u'í', 'i').replace(u'ó', 'o').replace(u'ú', 'u')
    usernamevariantfinal = ''
    for letra in usernamevariant:
        if letra in alfabeto:
            usernamevariantfinal += letra
    if variant > 1:
        usernamevariantfinal += str(variant)

    if not User.objects.filter(username=usernamevariantfinal).exclude(persona=persona).exists():
        return usernamevariantfinal
    else:
        return calculate_username(persona, variant + 1)

def convertirfecha(fecha):
    try:
        return date(int(fecha[6:10]), int(fecha[3:5]), int(fecha[0:2]))
    except Exception as ex:
        return datetime.now().date()

def convertirfechahora(fecha):
    try:
        return datetime(int(fecha[0:4]), int(fecha[5:7]), int(fecha[8:10]), int(fecha[11:13]), int(fecha[14:16]),
                        int(fecha[17:19]))
    except Exception as ex:
        return datetime.now()

def convertirfechahorainvertida(fecha):
    try:
        return datetime(int(fecha[6:10]), int(fecha[3:5]), int(fecha[0:2]), int(fecha[11:13]), int(fecha[14:16]),
                        int(fecha[17:19]))
    except Exception as ex:
        return datetime.now()


