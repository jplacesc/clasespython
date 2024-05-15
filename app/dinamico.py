# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, JsonResponse,HttpResponse
from django.shortcuts import render
from app.formularios import FacturaVentaFormaPagoForm,   FacturaVentaCabeceraForm, FacturaVentaDetalleForm
from app.models import FacturaVenta,FacturaVentaDetalle,Cliente, \
    FormaPago,FacturaVentaFormaPago,ItemUnidadMedidaStock,Item,UnidadMedida,\
    ItemUnidadMedida,AnioEjercicio,Vendedor,SucursalVendedor,ItemUnidadMedidaEquivalencia
from app.funciones import log, cargar_plantilla_base_simple, MiPaginador, convertir_fecha, convertir_fecha_hora, \
    convertir_fecha_hora_invertida,convertir_fecha_invertida
from datetime import datetime, timedelta
import json
from decimal import Decimal
from django.template.loader import get_template
from django.db.models import Sum
from app.funciones import round_half_up
from app.convertirhtml2pdf import conviert_html_to_pdf
from django.db.models import Q

@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    data = {}
    cargar_plantilla_base_simple(request, data)
    usuario = request.session['usuario']
    if 'action' in request.GET:
        action = request.GET['action']

        if action == 'sucursalvendedor':
            try:
                lista = []
                for sv in SucursalVendedor.objects.filter(status=True):
                    datadoc = {}
                    datadoc['Sucursal'] = sv.sucursal.nombre_completo()
                    datadoc['Vendedor'] = sv.vendedor.nombre_completo()
                    lista.append(datadoc)
                response = HttpResponse(json.dumps(lista), content_type="application/json")
                return response
            except Exception as ex:
                return JsonResponse({'result': 'bad', "mensaje": u"Error al obtener los datos"})

        elif action == 'factura':
            try:
                lista = []
                for factura in FacturaVenta.objects.filter(status=True):
                    datadoc = {}
                    datadoc['Factura'] = factura.numero
                    datadoc['Fecha'] = str(factura.fechafactura)
                    datadoc['Cliente'] = factura.cliente.nombre_completo()
                    datadoc['Vendedor'] = factura.vendedor.vendedor.nombre_completo()
                    datadoc['Estado'] = "Pagada" if factura.pagada else "Falta de pago"
                    lista.append(datadoc)
                response = HttpResponse(json.dumps(lista), content_type="application/json")
                return response
            except Exception as ex:
                return JsonResponse({'result': 'bad', "mensaje": u"Error al obtener los datos"})

        elif action == 'itemequivalencia':
            try:
                lista = []
                for equivalencia in ItemUnidadMedidaEquivalencia.objects.filter(status=True):
                    datadoc = {}
                    datadoc['Item'] = equivalencia.itemunidadmedida.item.nombre_completo()
                    datadoc['Unidad Medida'] = equivalencia.itemunidadmedida.unidad_medida.nombre_completo()
                    datadoc['Orden'] = str(equivalencia.orden)
                    datadoc['Valor origen'] = str(equivalencia.valorumorigen)
                    datadoc['Valor Fin'] = str(equivalencia.equivalenciaumfin)

                    lista.append(datadoc)
                response = HttpResponse(json.dumps(lista), content_type="application/json")
                return response
            except Exception as ex:
                return JsonResponse({'result': 'bad', "mensaje": u"Error al obtener los datos"})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        try:
            data['title'] = u'Reporte dinámico'
            return render(request, "dinamico/viewdinamico.html", data)
        except Exception as ex:
            return bad_json(mensaje=ex.__str__())