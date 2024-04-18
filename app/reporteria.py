# -*- coding: UTF-8 -*-
import json

from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, DELETION
from django.contrib.admin.utils import unquote
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.db import transaction, router
from django.forms import model_to_dict
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str
from xlwt import *

from app.formularios import *
from django.db import connection, transaction
from django.template import Context
import sys
from django.template.loader import get_template
from app.funciones import log, cargar_plantilla_base_simple, MiPaginador, convertir_fecha, convertir_fecha_hora,convertir_fecha_hora_invertida
from django.shortcuts import render, redirect

@login_required(redirect_field_name='ret', login_url='/loginsga')
@transaction.atomic()
def view(request):
    data = {}
    cargar_plantilla_base_simple(request,data)
    if request.method == 'POST':
        action = request.POST['action']

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'ventas_excel':
                try:
                    __author__ = 'Jussy'
                    style_nb = easyxf('font: name Times New Roman, color-index yellow, bold on', num_format_str='#,##0.00')
                    style_sb = easyxf('font: name Times New Roman, color-index yellow, bold on')
                    title = easyxf(
                        'font: name Times New Roman, color-index yellow, bold on , height 350; alignment: horiz centre')
                    style1 = easyxf(num_format_str='D-MMM-YY')
                    font_style = XFStyle()
                    font_style.font.bold = True
                    font_style2 = XFStyle()
                    font_style2.font.bold = False
                    wb = Workbook(encoding='utf-8')
                    ws = wb.add_sheet('facturas')
                    ws.write_merge(0, 0, 0, 5, 'Reporte de ventas diarias', title)
                    nombre = "ventas" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".xls"
                    response = HttpResponse(content_type="application/ms-excel")
                    response['Content-Disposition'] = 'attachment; filename=' + nombre

                    columns = [
                        (u"No.", 1000),
                        (u"Código Fact/Nota", 10000),
                        (u"Cantidad", 6000),
                        (u"Código de Item", 6000),
                        (u"Descripción Item", 6000),
                        (u"Subtotal", 10000),
                        (u"Costo", 10000),
                        (u"Compras", 10000),
                        (u"Ventas", 10000),
                        (u"Ganancia", 10000),
                        (u"Porcentaje", 10000),
                        (u"Total", 10000),
                    ]
                    row_num = 2
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num][0], font_style)
                        ws.col(col_num).width = columns[col_num][1]
                    row_num = 3
                    i = 0
                    fechadesde = datetime.now().date()
                    fechahasta = convertir_fecha_hora_invertida(str(datetime.now().date()) + " 23:59:59")
                    detallefacturas = FacturaVentaDetalle.objects.filter(Q(facturaventa__fechafactura__gte=fechadesde),
                                                                         Q(facturaventa__fechafactura__lte=fechahasta),
                                                                        status=True, facturaventa__valida=True)
                    total1 = 0
                    total2 = 0
                    total3 = 0
                    total4 = 0
                    auxiliar = 0
                    for detalle in detallefacturas:
                        i += 1
                        ws.write(row_num, 0, i, font_style2)
                        if auxiliar != detalle.facturaventa_id:
                            ws.write_merge(row_num, (int(row_num + detalle.facturaventa.cantidad_productos())) - 1, 1, 1,
                                           str(detalle.facturaventa.codigo), font_style2)
                        compras = round_half_up(
                            float(detalle.itemunidadmedidastock.costo_unitario) * float(detalle.cantidad), 4)
                        total1 += compras
                        ventas = round_half_up(float(detalle.subtotal) * float(1.12), 4)
                        total2 += ventas
                        ganancia = round_half_up(float(ventas) - float(compras), 4)
                        total3 += ganancia
                        porcentaje = round_half_up((float(ganancia) / float(ventas)) * 100, 4)
                        total4 += porcentaje
                        ws.write(row_num, 2, str(detalle.cantidad), font_style2)
                        ws.write(row_num, 3, str(detalle.itemunidadmedidastock.itemunidadmedida.item.codigo), font_style2)
                        ws.write(row_num, 4, str(detalle.itemunidadmedidastock.itemunidadmedida.item.descripcion),
                                 font_style2)
                        ws.write(row_num, 5, str(detalle.subtotal), font_style2)
                        ws.write(row_num, 6, str(detalle.itemunidadmedidastock.costo_unitario), font_style2)
                        ws.write(row_num, 7, u"%s" % compras, font_style2)
                        ws.write(row_num, 8, u"%s" % ventas, font_style2)
                        ws.write(row_num, 9, u"%s" % ganancia, font_style2)
                        ws.write(row_num, 10, u"%s" % porcentaje, font_style2)
                        if auxiliar != detalle.facturaventa_id:
                            ws.write_merge(row_num, (row_num + detalle.facturaventa.cantidad_productos()) - 1, 11, 11,
                                           str(detalle.facturaventa.total), font_style2)
                        row_num += 1
                        auxiliar = detalle.facturaventa_id

                    row_num += 1
                    ws.write(row_num, 7, total1, font_style2)
                    ws.write(row_num, 8, total2, font_style2)
                    ws.write(row_num, 9, total3, font_style2)
                    ws.write(row_num, 10, total4, font_style2)
                    wb.save(response)
                    return response
                except Exception as ex:
                    pass

            return HttpResponseRedirect(request.path)
        else:
            try:
                data['title'] = 'Reportería'
                return render(request, "reporteria/view.html", data)
            except Exception as ex:
                pass
