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

def importar_data():
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
                        facturaventa_id=(row[18]).strip()
                        impuesto_id=(row[19]).strip()
                        itemunidadmedidastock_id=(row[20]).strip()
                        subtotal_detalle=(row[21]).strip()
                        ganancia=(row[22]).strip()
                        porcentaje_ganancia=(row[23]).strip()
                        costo=(row[24]).strip()
                        forma_pago=(row[25]).strip()
                        eFacturaVenta=FacturaVenta.objects.filter(numero=numero)
                        if not eFacturaVenta.exists():
                            facturaventa = FacturaVenta(valida=True, numero=numero,
                                                    codigo=codigo,
                                                    cliente=cliente_id,
                                                    vendedor=vendedor_id,
                                                    fechafactura=fechafactura,
                                                    direccionentrega=direccionentrega,
                                                    valorimpuesto=valorimpuesto,
                                                    efectivorecibido=efectivorecibido,
                                                    cambio=cambio,
                                                    subtotal=subtotal,
                                                    valorimpuesto=valorimpuesto,
                                                    total=total
                                                    )
                            facturaventa.save()
                        else:
                            eFacturaVenta=eFacturaVenta.first()
                        fvfp = FacturaVentaFormaPago(
                            facturaventa=facturaventa,
                            formapago=formapagob if formapagob else None,
                            observacion=observacion,
                            valor=valor,
                        )
                        fvfp.save()
                        facturaventadetalle = FacturaVentaDetalle(
                            facturaventa=facturaventa,
                            itemunidadmedidastock=itemumstock,
                            cantidad=cantidad,
                            precio=precio,
                            subtotal=subtotal,
                            impuesto=item.impuesto,
                            valorimpuesto=valorimpuesto,
                            total=total,
                            porcentaje_ganancia=porcentajeganancia, ganancia=ganancia,
                            costo=itemumstock.costo_unitario
                        )
                        facturaventadetalle.save(request)
                        print(f"({total}/{contador}) Se guardo/actualizo: {ePerson.__str__()}")

                    except Exception as ex:
                        transaction.set_rollback(True)
                        print(f"Ocurrio un error {ex.__str__()}")

            contador += 1


importar_data()