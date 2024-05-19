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

def importar_data_csv():
    import os
    archivo = os.path.join(os.path.join(BASE_DIR,  'files', 'facturas Venta.csv'))
    with open(archivo, newline='', encoding="utf8") as File:
        reader = csv.reader(File, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        contador = 0
        total = 14000
        for row in reader:
            print(row)
            if contador > 0:
                with transaction.atomic():
                    try:
                        numero=(row[0]).strip()
                        codigo=(row[1]).strip()
                        cliente_id=(row[2]).strip()
                        vendedor_id=(row[3]).strip()
                        fechafactura=(row[4]).strip()
                        fechafactura=convertir_fecha_invertida(fechafactura)
                        direccionentrega=(row[5]).strip()
                        subtotal=(row[6]).strip()
                        valorimpuesto=(row[7]).strip()
                        total=(row[8]).strip()
                        efectivorecibido=(row[9]).strip()
                        cambio=(row[10]).strip()
                        valida=(row[11]).strip()
                        pagada=(row[12]).strip()
                        tipo=(row[13]).strip()
                        cantidad=(row[14]).strip()
                        precio=(row[15]).strip()
                        valorimpuestodetalle=(row[16]).strip()
                        totaldetalle=(row[17]).strip()
                        impuesto_id=(row[19]).strip()
                        itemunidadmedidastock_id=(row[20]).strip()
                        subtotal_detalle=(row[21]).strip()
                        ganancia=(row[22]).strip()
                        porcentaje_ganancia=(row[23]).strip()
                        costo=(row[24]).strip()
                        forma_pago=(row[25]).strip()

                        try:
                            eFacturaVenta=FacturaVenta.objects.get(numero=numero,codigo=codigo,fechafactura__date=fechafactura)
                        except ObjectDoesNotExist:
                            eFacturaVenta = FacturaVenta(valida=True, numero=numero,
                                                    codigo=codigo,
                                                    cliente_id=int(cliente_id),
                                                    vendedor_id=int(vendedor_id),
                                                    fechafactura=fechafactura,
                                                    direccionentrega=direccionentrega,
                                                    valorimpuesto=valorimpuesto,
                                                    efectivorecibido=efectivorecibido,
                                                    cambio=cambio,
                                                    subtotal=subtotal,
                                                    total=total
                                                    )
                            eFacturaVenta.save()
                        # EFECTIVO - 1019.1500
                        formasPago = forma_pago.split("-")
                        descripcionForma=formasPago[0]
                        valorForma=formasPago[1]
                        eFormaPago=FormaPago.objects.get(descripcion=descripcionForma)
                        eFacturaVentaFormaPago = FacturaVentaFormaPago(
                            facturaventa=eFacturaVenta,
                            formapago=eFormaPago,
                            observacion='migración',
                            valor=valorForma,
                        )
                        eFacturaVentaFormaPago.save()

                        eFacturaVentaDetalle = FacturaVentaDetalle(
                            facturaventa=eFacturaVenta,
                            itemunidadmedidastock_id=int(itemunidadmedidastock_id),
                            cantidad=cantidad,
                            precio=precio,
                            subtotal=subtotal,
                            impuesto_id=int(impuesto_id),
                            valorimpuesto=valorimpuesto,
                            total=totaldetalle,
                            porcentaje_ganancia=porcentaje_ganancia,
                            ganancia=ganancia,
                            costo=costo)
                        eFacturaVentaDetalle.save()
                        print(f"({total}/{contador}) Se guardo/actualizo: {eFacturaVenta.__str__()}")
                    except Exception as ex:
                        transaction.set_rollback(True)
                        print(f"Ocurrio un error {ex.__str__()}")
            contador += 1

# importar_data_csv()

def importar_data_excel():
    contador = 0
    miarchivo = openpyxl.load_workbook("files/facturasVenta.xlsx")
    lista = miarchivo.get_sheet_by_name('Hoja1')
    totallista = lista.rows
    for fila in totallista:
        contador += 1
        if contador>2:
            with transaction.atomic():
                try:
                    numero = (fila[0].value).strip()
                    codigo = (fila[1].value).strip()
                    cliente_id = (fila[2].value).strip()
                    vendedor_id = (fila[3].value).strip()
                    fechafactura = (fila[4].value).strip()
                    fechafactura = convertir_fecha_invertida(fechafactura)
                    direccionentrega = (fila[5].value).strip() if fila[5].value else ""
                    subtotal = (fila[6].value).strip()
                    valorimpuesto = (fila[7].value).strip()
                    total = (fila[8].value).strip()
                    efectivorecibido = (fila[9].value).strip()
                    cambio = (fila[10].value).strip()
                    valida = (fila[11].value).strip()
                    pagada = (fila[12].value).strip()
                    tipo = (fila[13].value).strip()
                    cantidad = (fila[14].value).strip()
                    precio = (fila[15].value).strip()
                    valorimpuestodetalle = (fila[16].value).strip()
                    totaldetalle = (fila[17].value).strip()
                    impuesto_id = (fila[19].value).strip()
                    itemunidadmedidastock_id = (fila[20].value).strip()
                    subtotal_detalle = (fila[21].value).strip()
                    ganancia = (fila[22].value).strip()
                    porcentaje_ganancia = (fila[23].value).strip()
                    costo = (fila[24].value).strip()
                    forma_pago = (fila[25].value).strip()
                    try:
                        eFacturaVenta = FacturaVenta.objects.get(numero=numero, codigo=codigo,
                                                                 fechafactura__date=fechafactura)
                    except ObjectDoesNotExist:
                        eFacturaVenta = FacturaVenta(valida=True, numero=numero,
                                                     codigo=codigo,
                                                     cliente_id=int(cliente_id),
                                                     vendedor_id=int(vendedor_id),
                                                     fechafactura=fechafactura,
                                                     direccionentrega=direccionentrega,
                                                     valorimpuesto=float(valorimpuesto.replace(',', '.')),
                                                     efectivorecibido=float(efectivorecibido.replace(',', '.')),
                                                     cambio=float(cambio.replace(',', '.')),
                                                     subtotal=float(subtotal.replace(',', '.')),
                                                     total=float(total.replace(',', '.'))
                                                     )
                        eFacturaVenta.save()
                    formasPago = forma_pago.split("-")
                    descripcionForma = formasPago[0]
                    valorForma = formasPago[1]
                    eFormaPago = FormaPago.objects.get(descripcion=descripcionForma)
                    eFacturaVentaFormaPago = FacturaVentaFormaPago(
                        facturaventa=eFacturaVenta,
                        formapago=eFormaPago,
                        observacion='migración',
                        valor=float(valorForma.replace(',', '.')),
                    )
                    eFacturaVentaFormaPago.save()

                    eFacturaVentaDetalle = FacturaVentaDetalle(
                        facturaventa=eFacturaVenta,
                        itemunidadmedidastock_id=int(itemunidadmedidastock_id),
                        cantidad=cantidad,
                        precio=float(precio.replace(',', '.')),
                        subtotal=float(subtotal.replace(',', '.')),
                        impuesto_id=int(impuesto_id),
                        valorimpuesto=float(valorimpuesto.replace(',', '.')),
                        total=float(totaldetalle.replace(',', '.')),
                        porcentaje_ganancia=float(porcentaje_ganancia.replace(',', '.')),
                        ganancia=float(ganancia.replace(',', '.')),
                        costo=float(costo.replace(',', '.')))
                    eFacturaVentaDetalle.save()
                    fila[26].value = "REGISTRO ACTUALIZADO"
                    print(f"({total}/{contador}) Se guardo/actualizo: {eFacturaVenta.__str__()}")
                except Exception as ex:
                    transaction.set_rollback(True)
                    print(f"Ocurrio un error {ex.__str__()}")

    print(f"Finalizo proceso ---")
    miarchivo.save("facturasVenta.xlsx")
    print("FIN: ", miarchivo)

# importar_data_excel()

# CONSULTAS

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
existe1=Item.objects.only("id").filter(status=True).exists()
# Selecciona el primer objeto de la clase Item que tenga el atributo status igual a True.
primerV1=Item.objects.filter(status=True).first()

primerV1 = Item.objects.filter(id=1000).first()

primerV1=Item.objects.filter(status=True).last()

primerV3 = Item.objects.filter(status=True)[0]

primerV4 = Item.objects.filter(status=True).order_by('-id')

total_devives = ItemUnidadMedidaStock.objects.filter(itemunidadmedida__item__marca_id=9, status=True).aggregate(total=Avg('stock'))['total']

facturaxfechas_promedio= FacturaVenta.objects.filter(status=True, fechafactura__gte='2023-05-01', fechafactura__lte='2025-05-10').aggregate(venta=(Avg(F('total'), output_field=FloatField()))).get('venta')

facturaxfechas_suma= FacturaVenta.objects.filter(status=True, fechafactura__gte='2023-05-01', fechafactura__lte='2025-05-10').aggregate(venta=(Sum(F('total'), output_field=FloatField()))).get('venta')

facturasxfecha = FacturaVenta.objects.filter(status=True, fechafactura__gte='2023-05-01', fechafactura__lte='2025-05-10')

facturasxcoincidencia = FacturaVenta.objects.filter(Q(numero__icontains='001') | Q(codigo__icontains='001'), status=True)

cantxcoincidencia = FacturaVenta.objects.filter(Q(numero__icontains='001') | Q(codigo__icontains='001'), status=True).count()

cantXcoincidenciaV1 = len(FacturaVenta.objects.filter(Q(numero__icontains='001') | Q(codigo__icontains='001'), status=True))

facturasV2 = FacturaVenta.objects.select_related().filter(status=True)

listaFacturas_lista= FacturaVenta.objects.values_list('id', flat=True).filter(status=True)

listaFacturas_lista2 = FacturaVenta.objects.values('id').filter(status=True)

facturasdevventas = FacturaVenta.objects.filter(status=True).annotate(es_efectivo=Exists(FacturaVentaFormaPago.objects.filter(status=True, formapago_id=2, facturaventa_id=OuterRef('id'))))

maximo = FacturaVenta.objects.filter(status=True).aggregate(max=Max('fechafactura'))['max']

minimo = FacturaVenta.objects.filter(status=True).aggregate(min=Min('fechafactura'))['min']
