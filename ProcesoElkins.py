#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import sys
import csv
import xlsxwriter
import xlwt
import openpyxl
import xlrd
from xlwt import *
YOUR_PATH = os.path.dirname(os.path.realpath(__file__))
SITE_ROOT = os.path.dirname(os.path.dirname(YOUR_PATH))

print(SITE_ROOT)
# your_djangoproject_home = os.path.dirname(os.path.realpath("sgan.settings.py"))
sys.path.append(SITE_ROOT)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
application = get_wsgi_application()

from app.settings import BASE_DIR
from django.db import transaction, connections, connection
from django.db.models import Q
from app.models import *
from time import sleep
from datetime import datetime, time
from django.core.exceptions import ObjectDoesNotExist
import hashlib
from app.funciones import convertir_fecha,convertir_fecha_invertida
from django.db.models import Func, Q, Avg, F,Count, Max, Sum, Exists, OuterRef,Min
from django.db.models import FloatField

# Selecciona un objeto de la clase UnidadMedida cuyo ID sea 11. Esta consulta espera exactamente un resultado y arrojará un error si no encuentra ningún objeto o si encuentra más de uno.
unidadMedida=UnidadMedida.objects.get(id=11)
# Selecciona todos los objetos de la clase UnidadMedida cuyo ID sea 11. Esta consulta devuelve un conjunto de objetos, que puede estar vacío si no se encuentra ningún objeto con el ID especificado.
unidadesMedida=UnidadMedida.objects.filter(id=11)
# Selecciona todos los objetos de la clase UnidadMedida que tengan el atributo status igual a True, y los ordena por el atributo unidad.
unidadesMedidas=UnidadMedida.objects.filter(status=True).order_by('unidad')
# Selecciona todos los objetos de la clase UnidadMedida y los ordena por el atributo unidad. Esta consulta devuelve todos los objetos de esa clase.
unidadesMedidas_1=UnidadMedida.objects.all().order_by('unidad')
# Selecciona solo el atributo id de todos los objetos de la clase Item cuyo status sea True.
soloid=Item.objects.only("id").filter(status=True)
# Verifica si hay al menos un objeto de la clase Item con el atributo status igual a True.
existe1=Item.objects.only("id").filter(id=10000).exists()
# Selecciona el primer objeto de la clase Item que tenga el atributo status igual a True.
primerV1=Item.objects.filter(status=True).first()
# Selecciona el ultimo objeto de la clase Item que tenga el atributo status igual a True.
primerV2=Item.objects.filter(status=True).last()
# Selecciona el primer objeto de la clase Item que tenga el atributo status igual a True. Esta consulta es similar a primer
primerv3=Item.objects.filter(status=True)[0]

primerv4=Item.objects.filter(status=True).order_by('id')[0]

total_devies = ItemUnidadMedidaStock.objects.filter(itemunidadmedida__item__marca_id=9, status=True).aggregate(total=Avg('stock'))['total']

facturasxfecha_promedio = FacturaVenta.objects.filter(status=True, fechafactura__gte='2023-05-01', fechafactura__lte='2025-05-10').aggregate(venta=(Avg(F('total'))))

facturaxfecha_suma=FacturaVenta.objects.filter(status=True, fechafactura__gte='2023-05-01', fechafactura__lte='2025-05-10').aggregate(venta=(Sum(F('total'), output_field=FloatField()))).get('venta')

facturaxfecha=FacturaVenta.objects.filter(status=True, fechafactura__gte='2023-05-01', fechafactura__lte='2025-05-10')

facturaxcoincidencia=FacturaVenta.objects.filter(Q(numero__icontains='001') | Q(codigo__icontains='001'),status=True)

cantxcoincidencia=FacturaVenta.objects.filter(Q(numero__icontains='001') | Q(codigo__icontains='001'),status=True).count()

cantxcoincidenciaV1= len(FacturaVenta.objects.filter(Q(numero__icontains='001') | Q(codigo__icontains='001'),status=True))

facturasv2 = FacturaVenta.objects.select_related().filter(status=True)

listafacturas_listas= FacturaVenta.objects.values_list('id', flat=True).filter(status=True)

listafacturas_lisv2= FacturaVenta.objects.values('id').filter(status=True)

facturasdeventa = FacturaVenta.objects.filter(status=True).annotate(es_efectivo=Exists(FacturaVentaFormaPago.objects.filter(status=True, formapago__id=2, facturaventa__id=OuterRef('id'))))

maximo = FacturaVenta.objects.filter(status=True).aggregate(mayor=Max('fechafactura'))['mayor']

minimo = FacturaVenta.objects.filter(status=True).aggregate(minimo=Min('fechafactura'))['minimo']
	