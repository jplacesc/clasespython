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

#importar_data_excel()

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
