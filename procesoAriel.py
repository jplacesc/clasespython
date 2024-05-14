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

unidadMedida=UnidadMedida.objects.get(id=11)
unidadesMedida=UnidadMedida.objects.filter(id=11)
unidadesMedidas=UnidadMedida.objects.filter(status=True).order_by('unidad')
unidadesMedidas_1=UnidadMedida.objects.all().order_by('unidad')
soloid=Item.objects.only('id').filter(status=True)
existe1=Item.objects.only('id').filter(id=10000).exists()
primerV1=Item.objects.filter(status=True).first()
primerV2=Item.objects.filter(status=True).last()
primerV3=Item.objects.filter(status=True)[0]
primerV4=Item.objects.filter(status=True).order_by('-id')[0]
total_devices=ItemUnidadMedidaStock.objects.filter(itemunidadmedida__item__marca_id=9, status=True).aggregate(total=Avg('stock'))['total']
facturaxfecha_promedio=FacturaVenta.objects.filter(staus=True,fechafactura__gte='2023-05-01',fechafactura__lte='2025-05-10').aggregate(venta=(Avg(F('total'),output_field=FloatField()))).get('venta')
facturaxfecha_suma=FacturaVenta.objects.filter(status=True, fechafactura__gte='2023-05-01', fechafactura__lte='2025-05-10').aggregate(venta=(Sum(F('total'), output_field=FloatField()))).get('venta')
facturaxfecha=FacturaVenta.objects.filter(status=True, fechafactura__gte='2023-05-01', fechafactura__lte='2025-05-10')
facturaxcoincidencia=FacturaVenta.objects.filter(Q(numero__icontains='001') | Q(codigo__icontains='001'),status=True)
cantxcoincidencia=FacturaVenta.objects.filter(Q(numero__icontains='001') | Q(codigo__icontains='001'),status=True).count()
cantxcoincidenciaV1=len(FacturaVenta.objects.filter(Q(numero__icontains='001') | Q(codigo__icontains='001'),status=True))
facturv2=FacturaVenta.objects.select_related().filter(status=True)
listafacturas_listas=FacturaVenta.objects.values_list('id', flat=True).filter(status=True)
listafacturas_lisv2=FacturaVenta.objects.values('id').filter(status=True)
facturasdevent =FacturaVenta.objects.filter(status=True).annotate(es_efectivo=Exists(FacturaVentaFormaPago.objects.filter(status=True, formapago__id=2, facturaventa__id=OuterRef('id'))))
maximo=FacturaVenta.objects.filter(statur=True).aggregate(maximo=Max('fechafactura'))['mayor']
minimo=FacturaVenta.objects.filter(status=True).aggregate(minimo=Min('fechafactura'))['minimo']