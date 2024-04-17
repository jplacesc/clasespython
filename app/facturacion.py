# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from app.formularios import FacturaVentaFormaPagoForm,   FacturaVentaCabeceraForm, FacturaVentaDetalleForm
from app.models import FacturaVenta,FacturaVentaDetalle,Cliente, \
    FormaPago,FacturaVentaFormaPago,ItemUnidadMedidaStock,Item,UnidadMedida,ItemUnidadMedida,AnioEjercicio,Vendedor
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
@transaction.atomic()
def view(request):
    data = {}
    cargar_plantilla_base_simple(request, data)
    anio = datetime.now().year
    anioejercicio = None
    vendedor = None
    sucursalvendedor = None
    data['hoy'] = hoy = datetime.now().date()
    data['usuario'] = usuario = request.session['usuario']
    data['sucursalsesion'] = sucursalsesion = request.session['sucursalsesion']
    if 'vendedor' in request.session:
        data['vendedor'] = vendedor = request.session['vendedor']
        if vendedor.obtener_sucursal():
            data['sucursalvendedor'] = sucursalvendedor = vendedor.obtener_sucursal()
        else:
            return HttpResponseRedirect('/?info=Usted no tiene asignado una sucursal.')
    else:
        return HttpResponseRedirect('/?info=Usted no esta configurado como vendedor.')
    if AnioEjercicio.objects.filter(anioejercicio=anio).exists():
        anioejercicio = AnioEjercicio.objects.filter(anioejercicio=anio)[0]
    else:
        anioejercicio = AnioEjercicio(anioejercicio=anio)
        anioejercicio.save()
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'addfactura':
            try:
                f = FacturaVentaCabeceraForm(request.POST)
                if f.is_valid():
                    formasdepago = json.loads(request.POST['lista_forma_pago'])
                    detalle = json.loads(request.POST['lista_items1'])
                    if not detalle:
                        return JsonResponse({"result": "bad", "mensaje": u"No ha ingresado items en el detalle de la factura."})
                    if not formasdepago:
                        return JsonResponse({"result": "bad", "mensaje": u"No ha ingresado forma(s) de pago para la factura."})
                    if int(f.cleaned_data['tipo']) == 1:
                        if FacturaVenta.objects.filter(status=True).exists():
                            facturaventa = FacturaVenta.objects.filter(status=True).order_by('-id')[0]
                            s = facturaventa.id + 1
                        else:
                            s=1
                        codigo = "NV"+str(s).zfill(9)
                    else:
                        secuencia=sucursalsesion.secuencia_factura()
                        secuencia.secuenciainicio += 1
                        secuencia.save(request)
                        s=secuencia.secuenciainicio
                        codigo = secuencia.establecimiento.strip() + "-" + secuencia.puntoemision.strip() + "-" + str(secuencia.secuenciainicio).zfill(9)
                        if FacturaVenta.objects.filter(status=True,valida=True,numero=secuencia.secuenciainicio).exists():
                            raise NameError(u"Numero de factura ya existe.")
                    if f.cleaned_data['cliente'] != 0:
                        cliente = Cliente.objects.get(id=f.cleaned_data['cliente'])
                    else:
                        raise NameError(u"Seleccione Cliente.")
                    facturaventa=FacturaVenta(valida=True,numero=s,
                                              codigo=codigo,
                                              cliente=cliente,
                                              vendedor=vendedor.pertenece_sucursal(sucursalsesion) if vendedor.pertenece_sucursal(sucursalsesion) else None,
                                              fechafactura=datetime.now(),
                                              direccionentrega=f.cleaned_data['direccionentrega'],
                                              efectivorecibido=float(request.POST['efectivorecibido']) if request.POST['efectivorecibido'] and request.POST['efectivorecibido'] != 'NaN'  else 0,
                                              cambio=float(request.POST['cambio']) if request.POST['cambio'] and request.POST['cambio'] != 'NaN' else 0,
                                              )
                    facturaventa.save(request)
                    totalformapago=0
                    for formapago in formasdepago:
                        formapagob=None
                        notacredito=None
                        idforma=0
                        idnota=0
                        idforma = int(formapago['idformapago'])
                        if idforma >0:
                            formapagob = FormaPago.objects.get(id=idforma)
                        valor = float(formapago['valor'])
                        observacion = formapago['observacion']

                        fvfp=FacturaVentaFormaPago(
                           facturaventa=facturaventa,
                            formapago=formapagob if formapagob else None,
                            observacion=observacion,
                            valor=valor,
                        )
                        fvfp.save(request)
                        if formapagob:
                            if not formapagob.numdias or formapagob.numdias == 0:
                                totalformapago+=valor

                    for d in detalle:
                        cantidadNueva = 0
                        itemumstock = None
                        itemunidadmedidafacturacompra = None
                        iddet=int(d['iddet'])
                        total=0
                        iva0=0
                        subtotal=0
                        impuesto=0
                        precio=0
                        descuento_aplicado = 0
                        if iddet == 0:
                            cantidad = int(d['cantidad'])
                            if cantidad < 1:
                                raise NameError(u"No puede ingresar cantidades menor a 1.")
                            item = Item.objects.get(pk=d['item'])
                            um = UnidadMedida.objects.get(pk=d['um'])
                            precio = 0
                            subtotal_unitario = 0
                            iva0 = 0
                            subtotal = 0
                            costoiva = 0
                            total = 0
                            valor_descuento_total = 0
                            costoiva = float(item.impuesto.valor)
                            precio = preciooriginal = float(d['precio'])
                            if costoiva > 0:
                                precio_costo_sin_iva = preciooriginal / (1 + (costoiva / 100))
                                subtotal = round_half_up(precio_costo_sin_iva * cantidad, 4)
                                iva0 = round_half_up(subtotal * (costoiva / 100), 4)
                                total = round_half_up(preciooriginal * cantidad, 2)
                            else:
                                subtotal = round_half_up(preciooriginal * cantidad, 4)
                                iva0 = 0
                                total = round_half_up(subtotal, 2)

                            total_cliente = float(d['total'])
                            if total_cliente!=total:
                                raise NameError(u"Error de cálculo en el total del item: %s"%(item))
                            valordcto = valor_descuento_total
                            subtotal = subtotal
                            valorimpuesto = iva0
                            porcentajeganancia=0
                            ganancia = 0
                            if ItemUnidadMedida.objects.filter(status=True, item=item, unidad_medida=um).exists():
                                itemunidadmedidafacturacompra = ItemUnidadMedida.objects.filter(status=True, item=item, unidad_medida=um)[0]
                                if ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida=itemunidadmedidafacturacompra, sucursal=sucursalsesion).exists():
                                    itemumstock = ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida=itemunidadmedidafacturacompra, sucursal=sucursalsesion)[0]
                                    if int(itemumstock.stock_actual()) < cantidad:
                                        raise NameError(u"Lo sentimos, el item %s solo dispone de %s  %s para facturar."%(itemumstock.itemunidadmedida.item.nombre_completo(),int(itemumstock.stock),itemumstock.itemunidadmedida.unidad_medida.nombre_completo()))
                                    ganancia = round_half_up(precio - float(itemumstock.costo_unitario), 4)
                                    porcentajeganancia = round_half_up((ganancia / precio) * 100, 4)
                                    facturaventadetalle = FacturaVentaDetalle(
                                        facturaventa=facturaventa,
                                        itemunidadmedidastock=itemumstock,
                                        cantidad=cantidad,
                                        precio=precio,
                                        subtotal=subtotal,
                                        impuesto=item.impuesto,
                                        valorimpuesto=valorimpuesto,
                                        descuento_aplicado=descuento_aplicado,
                                        descuento=valordcto,
                                        total=total,
                                        porcentaje_ganancia=porcentajeganancia,ganancia=ganancia,
                                        costo=itemumstock.costo_unitario
                                    )
                                    facturaventadetalle.save(request)

                        for itemunidadmedidabase in ItemUnidadMedida.objects.filter(status=True, item=item).order_by('-orden'):
                            cantidadstock = 0
                            stockorigen = None
                            if itemunidadmedidafacturacompra.orden <= itemunidadmedidabase.orden:
                                if itemunidadmedidafacturacompra.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidabase.unidad_medida, unidad_medida_fin=itemunidadmedidafacturacompra.unidad_medida).exists():
                                    equivalencia = itemunidadmedidafacturacompra.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidabase.unidad_medida, unidad_medida_fin=itemunidadmedidafacturacompra.unidad_medida)[0]
                                    cantidadNueva = cantidad / float(equivalencia.equivalenciaumfin)
                            else:
                                if itemunidadmedidabase.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidafacturacompra.unidad_medida, unidad_medida_fin=itemunidadmedidabase.unidad_medida).exists():
                                    equivalencia = itemunidadmedidabase.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidafacturacompra.unidad_medida, unidad_medida_fin=itemunidadmedidabase.unidad_medida)[0]
                                    cantidadNueva = cantidad * float(equivalencia.equivalenciaumfin)
                            if sucursalsesion.itemunidadmedidastock_set.filter(status=True, itemunidadmedida=itemunidadmedidabase).exists():
                                stockorigen = sucursalsesion.itemunidadmedidastock_set.filter(status=True, itemunidadmedida=itemunidadmedidabase)[0]
                                cantidad_antes=stockorigen.stock
                                resta = float(stockorigen.stock) - round_half_up(cantidadNueva,4)
                                if resta < 0:
                                    raise NameError(u"Error el ítem %s no tiene stock suficiente para procesar la factura, el resultado sería un valor negativo (%s)" % (stockorigen.itemunidadmedida,resta))
                                stockorigen.stock -= Decimal(cantidadNueva)
                                stockorigen.save(request)
                    total1=facturaventa.actualizar_valores_cabecera()
                    if round_half_up(float(totalformapago),2) >= round_half_up(float(total1),2):
                        facturaventa.pagada=True
                    sumaxformaspago= FacturaVentaFormaPago.objects.filter(facturaventa=facturaventa).aggregate(suma=Sum('valor'))['suma']
                    restafp=total1-sumaxformaspago
                    if int(restafp)!=0:
                        raise NameError( u"El total del detalle de las forma de pago no coincide con el valor total de la factura.")
                    facturaventa.save(request)
                    return JsonResponse({"result": "ok","id":facturaventa.id})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al emitir factura. %s"%ex})

        elif action == 'consulta_items':
            try:
                id=int(request.POST['id'])
                lista = []
                if id > 0:
                    orden = OrdenPedido.objects.get(pk=request.POST['id'])
                    if orden.ordenpedidodetalle_set.values('id').filter(status=True).exists():
                        for item in orden.ordenpedidodetalle_set.values('itemunidadmedidastock__itemunidadmedida__item_id','itemunidadmedidastock__itemunidadmedida__item__descripcion').filter(status=True, itemunidadmedidastock__itemunidadmedida__item__status=True).distinct('itemunidadmedidastock__itemunidadmedida__item__id'):
                            lista.append([item['itemunidadmedidastock__itemunidadmedida__item_id'], u'%s' % (item['itemunidadmedidastock__itemunidadmedida__item__descripcion']) ])
                else:
                    from django.db.models import F
                    if ItemUnidadMedidaStock.objects.values_list('itemunidadmedida__item_id').filter(status=True, sucursal=sucursalsesion, itemunidadmedida__item__status=True).exists():
                        for item in ItemUnidadMedidaStock.objects.values('itemunidadmedida__item_id','itemunidadmedida__item__descripcion','itemunidadmedida__item__codigo'
                                                                         ).filter(Q(stock__gte=1),
                                                                                  # Q(stock__gt=F('stockcomprometido')),
                                                                                  status=True, sucursal=sucursalsesion, itemunidadmedida__item__status=True).distinct('itemunidadmedida__item__id'):
                            lista.append([item['itemunidadmedida__item_id'], u'%s / %s' % (item['itemunidadmedida__item__codigo'],item['itemunidadmedida__item__descripcion'])])
                return JsonResponse({'result': 'ok', 'lista': lista})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'consulta_unidadmedida':
            try:
                lista = []
                item = Item.objects.get(pk=request.POST['id'])
                if request.POST['idorden']!='NaN':
                    orden = OrdenPedido.objects.get(id=int(request.POST['idorden']))
                    if orden.ordenpedidodetalle_set.values('id').filter(status=True).exists():
                        for ordend in orden.ordenpedidodetalle_set.values('itemunidadmedidastock__itemunidadmedida__unidad_medida_id', 'itemunidadmedidastock__itemunidadmedida__unidad_medida__descripcion').filter(status=True, itemunidadmedidastock__sucursal=sucursalsesion,
                                                                                                                                                                                                                     itemunidadmedidastock__itemunidadmedida__item=item).distinct(
                            'itemunidadmedidastock__itemunidadmedida__unidad_medida_id'):
                            lista.append([ordend['itemunidadmedidastock__itemunidadmedida__unidad_medida_id'], u'%s' % (ordend['itemunidadmedidastock__itemunidadmedida__unidad_medida__descripcion'])])
                else:
                    if item.itemunidadmedida_set.filter(status=True).exists():
                        for um in item.itemunidadmedida_set.filter(status=True).order_by('orden'):
                            lista.append([um.unidad_medida.id, um.unidad_medida.descripcion])
                return JsonResponse({'result': 'ok', 'lista': lista,'unidad_base':item.unidad_base_id})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'consulta_precio':
            try:
                item = Item.objects.get(pk=request.POST['iditem'])
                um = UnidadMedida.objects.get(pk=request.POST['idum'])
                if ItemUnidadMedida.objects.filter(status=True, item=item, unidad_medida=um).exists():
                    itemunidadmedida = ItemUnidadMedida.objects.filter(status=True, item=item, unidad_medida=um)[0]
                    if ItemUnidadMedidaStock.objects.values('id').filter(status=True, itemunidadmedida=itemunidadmedida, sucursal=sucursalsesion).exists():
                        itemumstock = ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida=itemunidadmedida, sucursal=sucursalsesion)[0]

                        # return JsonResponse({"result": "ok", "precio": itemumstock.precio, "stock": int(itemumstock.stock - itemumstock.stockcomprometido) if itemumstock.stock > itemumstock.stockcomprometido and itemumstock.stock >= 1 else 0})
                        return JsonResponse({"result": "ok", "precio": itemumstock.precio, "stock": int(itemumstock.stock) if itemumstock.stock >= 1 else 0})
                    else:
                        return JsonResponse({"result": "ok", "precio": 0, "impuesto": 0, "stock": 0})
                else:
                    return JsonResponse({"result": "ok", "valor": 0, "impuesto": 0})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'consulta_precio_minimo':
            try:
                item = Item.objects.get(pk=request.POST['iditem'])
                um = UnidadMedida.objects.get(pk=request.POST['idum'])
                valor = float(request.POST['valor'])
                if ItemUnidadMedida.objects.filter(status=True, item=item, unidad_medida=um).exists():
                    itemunidadmedida = ItemUnidadMedida.objects.filter(status=True, item=item, unidad_medida=um)[0]
                    if ItemUnidadMedidaStock.objects.values('id').filter(status=True, itemunidadmedida=itemunidadmedida, sucursal=sucursalsesion).exists():
                        itemumstock = ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida=itemunidadmedida, sucursal=sucursalsesion)[0]
                        if valor < float(itemumstock.preciominimo):
                            return JsonResponse({"result": "novalido", "mensaje": u"Precio invalido, el valor mínimo es: %s."%itemumstock.preciominimo, "precio":itemumstock.preciominimo})
                        if itemumstock.preciominimo <=0:
                            return JsonResponse({"result": "novalido",
                                                 "mensaje": u"Precio invalido, el precio mínimo configurado es: %s." % itemumstock.preciominimo,
                                                 "precio": itemumstock.preciominimo})
                        else:
                            return JsonResponse({"result": "valido", "mensaje": u".."})
                    else:
                        return JsonResponse({"result": "novalido", "mensaje": u"Este item no esta en existencias."})
                else:
                    return JsonResponse({"result": "novalido", "mensaje": u"Este item no tiene asignado unidad de media"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'detalleformapago':
            try:
                facturaventa = FacturaVenta.objects.get(pk=request.POST['id'])
                template = get_template("facturacion/detalleformapago.html")
                json_content = template.render({'facturaventa': facturaventa})
                return JsonResponse({"result": "ok", 'html': json_content})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'detalleProductos':
            try:
                facturaventa = FacturaVenta.objects.get(pk=request.POST['id'])
                template = get_template("facturacion/detalleproductos.html")
                json_content = template.render({'facturaventa': facturaventa})
                return JsonResponse({"result": "ok", 'html': json_content})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})


        elif action == 'consulta_equivalencia':
            try:
                lista = []
                item = Item.objects.get(pk=request.POST['item'])
                unidad = UnidadMedida.objects.get(pk=request.POST['unidad'])
                cantidad = float(request.POST['cantidad'])
                itemunidadmedidadestino = ItemUnidadMedida.objects.filter(status=True, item=item, unidad_medida=unidad)[0]
                equivalencia = None
                cantidadNueva = 0
                for itemunidadmedidabase in ItemUnidadMedida.objects.filter(status=True, item=item).order_by('-orden'):
                    if itemunidadmedidadestino.orden <= itemunidadmedidabase.orden:
                        if itemunidadmedidadestino.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidabase.unidad_medida, unidad_medida_fin=itemunidadmedidadestino.unidad_medida).exists():
                            equivalencia = itemunidadmedidadestino.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidabase.unidad_medida, unidad_medida_fin=itemunidadmedidadestino.unidad_medida)[0]
                            cantidadNueva = cantidad / float(equivalencia.equivalenciaumfin)
                            lista.append([itemunidadmedidabase.unidad_medida_id, cantidadNueva])
                    else:
                        if itemunidadmedidabase.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidadestino.unidad_medida, unidad_medida_fin=itemunidadmedidabase.unidad_medida).exists():
                            equivalencia = itemunidadmedidabase.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidadestino.unidad_medida, unidad_medida_fin=itemunidadmedidabase.unidad_medida)[0]
                            cantidadNueva = cantidad * float(equivalencia.equivalenciaumfin)
                            lista.append([itemunidadmedidabase.unidad_medida_id, cantidadNueva])

                return JsonResponse({'result': 'ok', 'lista': lista})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'cambia_estado_pago_factura':
            try:
                facturaventa = FacturaVenta.objects.get(pk=request.POST['id'])
                if facturaventa.pagada:
                    facturaventa.pagada=False
                else:
                    facturaventa.pagada=True
                facturaventa.save(request)
                return JsonResponse({"result": "ok"})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'addfactura':
                try:
                    data['title'] = u'Ingreso de Factura de Venta'
                    form = FacturaVentaCabeceraForm(initial={ 'cliente': 1})
                    form.adicionar_cabecera()
                    data['form'] = form

                    formdetalle = FacturaVentaDetalleForm()
                    formdetalle.adicionar(sucursalsesion)
                    data['formdetalle'] = formdetalle
                    data['sucursalsesion'] = sucursalsesion

                    form2 = FacturaVentaFormaPagoForm()
                    form2.adicionar()
                    data['formformapago'] = form2
                    data['limiteitems']= 13
                    return render(request, "facturacion/addfactura.html", data)
                except Exception as ex:
                    pass

            elif action == 'detallefacturas':
                try:
                    data['factura'] = factura = FacturaVenta.objects.get(pk=request.GET['id'])
                    data['title'] = u'Detalle de factura'
                    data['detalle'] = factura.facturaventadetalle_set.filter(status=True)
                    return render(request, "facturacion/detallefacturas.html", data)
                except Exception as ex:
                    pass

            elif action == 'detallepagos':
                try:
                    data['factura'] = factura = FacturaVenta.objects.get(pk=request.GET['id'])
                    data['saldo_factura'] = u'Saldo por Pagar %s' % (round_half_up(float(factura.valor_por_pagar()),2) if factura.valor_por_pagar()  > 0 else 0)
                    data['title'] = u'Detalle de Pagos'
                    data['detalle'] = factura.facturaventapago_set.filter(status=True)
                    return render(request, "facturacion/detallepagos.html", data)
                except Exception as ex:
                    pass

            elif action == 'addfacturapago':
                try:
                    if sesioncaja:
                        if sesioncaja.fecha.date() == hoy:
                            data['title'] = u'Agregar Pago de Factura'
                            data['factura'] = factura = FacturaVenta.objects.get(status=True, pk=request.GET['id'])
                            form = FacturaVentaPagoForm()
                            form.asignar_saldo(factura.valor_por_pagar(),factura.cliente)
                            data['valorapagar']=factura.valor_por_pagar()
                            data['form'] = form
                            return render(request, "facturacion/addfacturapago.html", data)
                except Exception as ex:
                    pass

            elif action == 'editfacturapago':
                try:
                    data['title'] = u'Editar pago de factura'
                    valorpagado = 0
                    data['factura'] = factura = FacturaVentaPago.objects.get(status=True, pk=request.GET['id'])
                    if FacturaVentaPago.objects.filter(facturaventa=factura.facturaventa, status=True).exclude(id=factura.id).exists():
                        valorpagado = FacturaVentaPago.objects.filter(facturaventa=factura.facturaventa, status=True).distinct().exclude(id=factura.id).aggregate(suma=Sum('valor'))['suma']
                    valorpagar = factura.facturaventa.total - valorpagado
                    # initial = model_to_dict(factura)
                    form = FacturaVentaPagoForm(initial={
                        'documentoreferencia': factura.documentoreferencia,
                        'formapago': factura.formapago,
                        'fecha': factura.fecha,
                        'archivo': factura.archivo,
                        'valor': valorpagar})
                    data['form'] = form
                    return render(request, "facturacion/editfacturapago.html", data)
                except Exception as ex:
                    pass

            elif action == 'deletefacturapago':
                try:
                    data['title'] = u'Eliminar pago de factura'
                    data['factura'] = FacturaVentaPago.objects.get(pk=request.GET['id'])
                    return render(request, "facturacion/deletefacturapago.html", data)
                except Exception as ex:
                    pass

            elif action == 'imprimir_factura':
                try:
                    data['factura'] =fv= FacturaVenta.objects.get(pk=request.GET['id'])
                    data['detalle'] = fv.facturaventadetalle_set.filter(status=True)

                    return conviert_html_to_pdf(
                        'facturacion/imprimir_factura.html',
                        {
                            'data': data,
                        }
                    )
                except Exception as ex:
                    pass


            elif action == 'consulta_valor_descuento':
                try:
                    oferta = OfertaItem.objects.get(status=True, pk=request.GET['id'])
                    return JsonResponse({'result': 'ok', 'valor': oferta.porcentajedescuento})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            elif action == 'calcular_costos_orden':
                try:
                    iddet=int(request.GET['iddet']) if request.GET['iddet'] else 0
                    cantidad = float(request.GET['cantidad'])
                    detalle = OrdenPedidoDetalle.objects.get(id=iddet)
                    precio = 0
                    subtotal_unitario = 0
                    iva0 = 0
                    subtotal = 0
                    costoiva=float(detalle.itemunidadmedidastock.itemunidadmedida.item.impuesto.valor)
                    preciooriginal = float(detalle.itemunidadmedidastock.precio if detalle.itemunidadmedidastock.precio else 0)
                    total=0
                    valor_descuento_total=0

                    if detalle.descuento_aplicado > 0:
                        precio = float(detalle.descuento_aplicado)
                        if costoiva > 0:
                            precio_descuento_sin_iva = precio / (1 + (costoiva / 100))
                            precio_costo_sin_iva =preciooriginal / (1 + (costoiva / 100))
                            valor_descuento_unitario=precio_costo_sin_iva-precio_descuento_sin_iva
                            subtotal = round_half_up(precio_costo_sin_iva * cantidad,4)
                            valor_descuento_total=round_half_up(valor_descuento_unitario*cantidad,4)
                            valor_antes_iva=subtotal-valor_descuento_total
                            iva0=round_half_up(valor_antes_iva*(costoiva / 100),4)
                            total = round_half_up(valor_antes_iva+iva0, 4)
                        else:
                            valor_descuento_unitario = preciooriginal - precio
                            subtotal = round_half_up(preciooriginal * cantidad, 4)
                            valor_descuento_total = round_half_up(valor_descuento_unitario * cantidad, 4)
                            valor_antes_iva = subtotal - valor_descuento_total
                            iva0 = 0
                            total = round_half_up(valor_antes_iva + iva0, 4)
                    else:
                        if costoiva > 0:
                            precio_costo_sin_iva = preciooriginal / (1 + (costoiva / 100))
                            subtotal = round_half_up(precio_costo_sin_iva * cantidad, 2)
                            iva0 = round_half_up(subtotal * (costoiva / 100), 4)
                            total = round_half_up(preciooriginal * cantidad, 4)
                        else:
                            subtotal = round_half_up(preciooriginal * cantidad, 2)
                            iva0 = 0
                            total = round_half_up(subtotal, 4)
                    return JsonResponse({'result': 'ok', 'iva0': iva0,'subtotal':subtotal,'total':total,'precio':precio,'valordcto':valor_descuento_total})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            elif action == 'calcular_costos_factura_venta':
                try:
                    precio=0
                    cantidad = float(request.GET['cantidad'])
                    subtotal_unitario = 0
                    iva0 = 0
                    subtotal = 0
                    costoiva =0
                    total=0
                    valor_descuento_total=0
                    if request.GET['iditem'] !='NaN' and request.GET['idum'] !='NaN':
                        item = Item.objects.get(pk=request.GET['iditem'])
                        costoiva=float(item.impuesto.valor)
                        precio=preciooriginal=float(request.GET['precio'])
                        if costoiva > 0:
                            precio_costo_sin_iva = preciooriginal / (1 + (costoiva / 100))
                            subtotal = round_half_up(precio_costo_sin_iva*cantidad,4)
                            iva0 = round_half_up(subtotal * (costoiva / 100), 4)
                            total = round_half_up(preciooriginal * cantidad, 2)
                        else:
                            subtotal = round_half_up(preciooriginal * cantidad,4)
                            iva0 = 0
                            total = round_half_up(subtotal, 2)
                    return JsonResponse({'result': 'ok', 'iva0': iva0,'subtotal':subtotal,'total':total,'precio':precio,'valordcto':valor_descuento_total})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            elif action == 'calcular_costos_devolucion':
                try:
                    iddet=int(request.GET['iddet']) if request.GET['iddet'] else 0
                    detalle=FacturaVentaDetalle.objects.get(id=iddet)
                    precio=0
                    cantidad = float(request.GET['cantidad'])
                    subtotal_unitario = 0
                    iva0 = 0
                    subtotal = 0
                    costoiva =0
                    total=0
                    valor_descuento_total=0
                    if detalle.descuento_aplicado > 0:
                        precio = float(detalle.descuento_aplicado)
                        costoiva=float(detalle.itemunidadmedidastock.itemunidadmedida.item.impuesto.valor)
                        preciooriginal=float(detalle.itemunidadmedidastock.itemunidadmedida.stock(detalle.facturaventa.vendedor.sucursal).precio if detalle.itemunidadmedidastock.itemunidadmedida.stock(detalle.facturaventa.vendedor.sucursal) else 0)
                        if costoiva > 0:
                            precio_descuento_sin_iva = precio / (1 + (costoiva / 100))
                            precio_costo_sin_iva =preciooriginal / (1 + (costoiva / 100))
                            valor_descuento_unitario=precio_costo_sin_iva-precio_descuento_sin_iva
                            subtotal = round_half_up(precio_costo_sin_iva * cantidad,4)
                            valor_descuento_total=round_half_up(valor_descuento_unitario*cantidad,4)
                            valor_antes_iva=subtotal-valor_descuento_total
                            iva0=round_half_up(valor_antes_iva*(costoiva / 100),4)
                            total = round_half_up(valor_antes_iva+iva0, 4)
                        else:
                            valor_descuento_unitario = preciooriginal - precio
                            subtotal = round_half_up(preciooriginal * cantidad, 4)
                            valor_descuento_total = round_half_up(valor_descuento_unitario * cantidad, 4)
                            valor_antes_iva = subtotal - valor_descuento_total
                            iva0 = 0
                            total = round_half_up(valor_antes_iva + iva0, 4)
                    else:
                        costoiva=float(detalle.itemunidadmedidastock.itemunidadmedida.item.impuesto.valor)
                        preciooriginal=precio=float(detalle.precio)
                        if costoiva > 0:
                            precio_costo_sin_iva = preciooriginal / (1 + (costoiva / 100))
                            subtotal = round_half_up(precio_costo_sin_iva*cantidad,4)
                            iva0 = round_half_up(subtotal * (costoiva / 100), 4)
                            total = round_half_up(preciooriginal * cantidad, 4)
                        else:
                            subtotal = round_half_up(preciooriginal * cantidad,4)
                            iva0 = 0
                            total = round_half_up(subtotal, 4)
                    return JsonResponse({'result': 'ok', 'iva0': iva0,'subtotal':subtotal,'total':total,'precio':precio,'valordcto':valor_descuento_total})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})


            elif action == 'detalleorden':
                try:
                    data['orden'] =orden = OrdenPedido.objects.get(pk=request.GET['id'])
                    data['title'] = u'Detalle de Orden de Pedido'
                    data['detalles'] = orden.ordenpedidodetalle_set.filter(status=True)
                    return render(request, "facturacion/detalleorden.html", data)
                except Exception as ex:
                    pass

            elif action == 'devoluciones':
                try:
                    data['factura'] = factura = FacturaVenta.objects.get(pk=request.GET['id'])
                    data['title'] = u'Devoluciones de factura %s' % factura
                    data['devoluciones'] = FacturaVentaDevolucionDetalle.objects.filter(status=True, facturaventadetalle__facturaventa=factura).order_by('-fecha_ins').distinct()
                    return render(request, "facturacion/devoluciones.html", data)
                except Exception as ex:
                    pass
            elif action == 'notascredito':
                try:
                    data['factura'] = factura = FacturaVenta.objects.get(pk=request.GET['id'])
                    data['title'] = u'Historial de Notas de crédito'
                    data['detallesnota'] = factura.notacredito_set.filter(status=True)
                    return render(request, "facturacion/notascredito.html", data)
                except Exception as ex:
                    pass

            elif action == 'adddevolucionfactura':
                try:
                    if sesioncaja:
                        if sesioncaja.fecha.date() == hoy:
                            data['title'] = u'Adicionar devolución'
                            data['factura'] = factura = FacturaVenta.objects.get(pk=request.GET['idfact'])
                            data['detalles'] = factura.facturaventadetalle_set.filter(status=True)
                            data['form'] = FacturaVentaDevolucionForm(initial={'documento_origen': factura})
                            return render(request, "facturacion/addevolucionfactura.html", data)
                except Exception as ex:
                    pass

            elif action == 'anular':
                try:
                    data['title'] = u'Anular Factura'
                    data['factura'] =factura= FacturaVenta.objects.get(pk=request.GET['id'])
                    if usuario.is_superuser:
                        data['form'] = FacturaCanceladaForm()
                        return render(request, "facturacion/anular.html", data)
                    else:
                        if hoy == factura.fechafactura.date():
                            data['form'] = FacturaCanceladaForm()
                            return render(request, "facturacion/anular.html", data)
                        else:
                            pass
                except Exception as ex:
                    pass

            elif action == 'imprimir_cancelar':
                try:
                    data['title'] = u'Imprimir / Cancelar Factura'
                    data['factura'] = factura = FacturaVenta.objects.get(status=True, pk=request.GET['id'])
                    return render(request, "facturacion/imprimir_cancelar.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(request.path)

        else:
            try:
                data['tite'] = u'Facturación'
                filtros, s, url_vars, id,estado,fecha = Q(), request.GET.get('s', ''), '', request.GET.get('id', '0'),request.GET.get('estado', '0'),request.GET.get('fecha', '')
                if usuario.is_superuser:
                    eFacturaVenta = FacturaVenta.objects.filter(status=True)
                elif vendedor:
                    eFacturaVenta = FacturaVenta.objects.filter(status=True,
                                                           vendedor__sucursal=vendedor.obtener_sucursal().sucursal)
                if int(id):
                    filtros = filtros & (Q(id=id))
                    data['id'] = f"{id}"
                    url_vars += f"&id={id}"
                if s:
                    filtros = filtros & (Q(cliente__nombre__icontains=s) | Q(cliente__apellido__icontains=s))
                    data['s'] = f"{s}"
                    url_vars += f"&s={s}"
                if estado:
                    estado_select= int(estado)
                    if estado_select >0:
                        if estado_select==1:
                            filtros = filtros & (Q(pagada=True))
                        elif estado_select==2:
                            filtros = filtros & (Q(pagada=True))

                if fecha!='':
                    fecha=convertir_fecha(request.GET['fecha'])
                    fechafin=convertir_fecha_hora("%s 23:59:59"%request.GET['fecha'])
                    filtros = filtros & (Q(fechafactura__gte=fecha,fechafactura__lte=fechafin))
                else:
                    fechafin = convertir_fecha_hora_invertida("%s 23:59:59" % hoy)
                    fecha = hoy
                    filtros = filtros & (Q(fechafactura__gte=fecha, fechafactura__lte=fechafin))
                data['fecha']=convertir_fecha_invertida(str(fecha)) if fecha else ""
                if filtros:
                    eFacturaVenta = eFacturaVenta.filter(filtros).order_by('fechafactura')
                paging = MiPaginador(eFacturaVenta, 15)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session:
                        paginasesion = int(request.session['paginador'])
                    if 'page' in request.GET:
                        p = int(request.GET['page'])
                    else:
                        p = paginasesion
                    try:
                        page = paging.page(p)
                    except:
                        p = 1
                    page = paging.page(p)
                except:
                    page = paging.page(p)
                request.session['paginador'] = p
                data['paging'] = paging
                data['page'] = page
                data['rangospaging'] = paging.rangos_paginado(p)
                data['facturas'] = page.object_list
                data['url_vars'] = url_vars
                return render(request, "facturacion/view.html", data)
            except Exception as ex:
                pass