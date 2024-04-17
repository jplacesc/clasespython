# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from app.models import ItemUnidadMedidaStock,ItemUnidadMedidaEquivalencia, Item,ItemUnidadMedida,Sucursal
from app.funciones import log, cargar_plantilla_base_simple, MiPaginador,round_half_up
from django.template.loader import get_template
from decimal import Decimal
@login_required(redirect_field_name='ret', login_url='/login')
@transaction.atomic()
def view(request):
    data = {}
    cargar_plantilla_base_simple(request, data)
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'detallestock':
            try:
                stock = ItemUnidadMedidaStock.objects.get(pk=request.POST['iddet'])
                respaldo = ItemUnidadMedidaStockRespaldo.objects.filter(status=True,
                                                                        itemunidadmedida=stock.itemunidadmedida,
                                                                        sucursal=stock.sucursal)
                template = get_template("view_stock/detallestock.html")
                json_content = template.render({'respaldo': respaldo})
                return JsonResponse({"result": "ok", 'html': json_content})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'cambiar_valorcosto_unitario':
            try:
                stock = ItemUnidadMedidaStock.objects.get(pk=int(request.POST['id']))
                porcentajeganancia = float(request.POST['porcentajeganancia'])
                costoform = float(request.POST['costo'])
                precio = float(request.POST['precio'])
                ganancia = 0
                if porcentajeganancia > 0:
                    precio = round_half_up(costoform / (1 - (porcentajeganancia / 100)), 4)
                    ganancia = round_half_up(precio - costoform, 4)
                else:
                    ganancia = round_half_up(precio - costoform, 4)
                    porcentajeganancia = round_half_up((ganancia / precio) * 100, 4)
                if precio < costoform:
                    raise NameError(u"El precio máximo no puede ser menor al costo: %s" % stock)

                stock.costo_unitario = costoform
                stock.ganancia = ganancia
                stock.precio = precio
                stock.porcentaje_ganancia = porcentajeganancia
                stock.save(request)
                return JsonResponse({'result': 'ok','costo':stock.costo_unitario,'porcentaje_ganancia': stock.porcentaje_ganancia, 'precio': stock.precio, 'ganancia': stock.ganancia})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', "mensaje": u"Error al actualizar costo. %s"%ex})

        elif action == 'cambiar_valorporcentaje_ganancia':
            try:
                stock = ItemUnidadMedidaStock.objects.get(pk=int(request.POST['id']))
                porcentajeganancia = float(request.POST['porcentajeganancia'])
                costoform = float(request.POST['costo'])
                precio = float(request.POST['precio'])
                ganancia = 0
                if porcentajeganancia > 0:
                    precio = round_half_up(costoform / (1 - (porcentajeganancia / 100)), 4)
                    ganancia = round_half_up(precio - costoform, 4)
                else:
                    ganancia = round_half_up(precio - costoform, 4)
                    porcentajeganancia = round_half_up((ganancia / precio) * 100, 4)

                if precio < costoform:
                    raise NameError(u"El precio máximo no puede ser menor al costo: %s" % stock)

                stock.costo_unitario = costoform
                stock.ganancia = ganancia
                stock.precio = precio
                stock.porcentaje_ganancia = porcentajeganancia
                stock.save(request)
                return JsonResponse({'result': 'ok','costo':stock.costo_unitario,'porcentaje_ganancia': stock.porcentaje_ganancia, 'precio': stock.precio, 'ganancia': stock.ganancia})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', "mensaje": u"Error al actualizar costo. %s"%ex})


        elif action == 'cambiar_valorprecio':
            try:
                stock = ItemUnidadMedidaStock.objects.get(pk=int(request.POST['id']))
                porcentajeganancia = float(request.POST['porcentajeganancia'])
                costoform = float(request.POST['costo'])
                precio = float(request.POST['precio'])
                if precio < costoform:
                    raise NameError(u"El precio máximo no puede ser menor al costo: %s" % stock)
                ganancia = 0
                if precio > 0:
                    ganancia = round_half_up(precio - costoform, 4)
                    porcentajeganancia = round_half_up((ganancia / precio) * 100, 4)
                else:
                    precio = round_half_up(costoform / (1 - (porcentajeganancia / 100)), 4)
                    ganancia = round_half_up(precio - costoform, 4)

                stock.ganancia = ganancia
                stock.precio = precio

                stock.porcentaje_ganancia = porcentajeganancia
                stock.save(request)
                return JsonResponse({'result': 'ok', 'porcentaje_ganancia': stock.porcentaje_ganancia, 'precio': stock.precio, 'ganancia': stock.ganancia})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', "mensaje": u"Error al actualizar costo. %s"%ex})

        elif action == 'cambiar_valorpreciominimo':
            try:
                stock = ItemUnidadMedidaStock.objects.get(pk=int(request.POST['id']))
                precio = float(request.POST['precio'])
                if precio < stock.costo_unitario:
                    raise NameError(u"El precio minimo no puede ser menor al costo: %s" % stock)
                stock.preciominimo = precio
                stock.save(request)
                return JsonResponse({'result': 'ok', 'preciominimo': stock.preciominimo})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', "mensaje": u"Error al actualizar costo. %s"%ex})

        elif action == 'cambiar_valor_stock':
            try:
                stock1 = ItemUnidadMedidaStock.objects.get(pk=int(request.POST['id']))
                itemunidadmedidafacturacompra=stock1.itemunidadmedida
                cantidad = float(request.POST['stock'])
                cantidadstock=0
                lista=[]
                lista1=[]
                for itemunidadmedidabase in ItemUnidadMedida.objects.filter(status=True, item=stock1.itemunidadmedida.item).order_by('-orden'):
                    cantidadstock = 0
                    if itemunidadmedidafacturacompra.orden <= itemunidadmedidabase.orden:
                        if itemunidadmedidafacturacompra.itemunidadmedidaequivalencia_set.filter(
                                status=True,
                                unidad_medida_origen=itemunidadmedidabase.unidad_medida,
                                unidad_medida_fin=itemunidadmedidafacturacompra.unidad_medida).exists():
                            equivalencia = itemunidadmedidafacturacompra.itemunidadmedidaequivalencia_set.filter(
                                status=True,
                                unidad_medida_origen=itemunidadmedidabase.unidad_medida,
                                unidad_medida_fin=itemunidadmedidafacturacompra.unidad_medida)[0]
                            cantidadstock = cantidad / float(equivalencia.equivalenciaumfin)
                    else:
                        if itemunidadmedidabase.itemunidadmedidaequivalencia_set.filter(status=True,
                                                                                        unidad_medida_origen=itemunidadmedidafacturacompra.unidad_medida,
                                                                                        unidad_medida_fin=itemunidadmedidabase.unidad_medida).exists():
                            equivalencia = itemunidadmedidabase.itemunidadmedidaequivalencia_set.filter(status=True,
                                                                                                        unidad_medida_origen=itemunidadmedidafacturacompra.unidad_medida,
                                                                                                        unidad_medida_fin=itemunidadmedidabase.unidad_medida)[0]
                            cantidadstock = cantidad * float(equivalencia.equivalenciaumfin)
                    stockante = ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida=itemunidadmedidabase, sucursal=stock1.sucursal)[0]
                    stockante.stock=Decimal(cantidadstock)
                    stockante.save(request)
                for itemunidadmedidabase in ItemUnidadMedida.objects.filter(status=True, item=stock1.itemunidadmedida.item).order_by('-orden'):
                    stockante2 = ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida=itemunidadmedidabase, sucursal=stock1.sucursal)[0]
                    lista.append([stockante2.id,stockante2.stock])
                    lista1.append([stockante2.id,stockante2.stock_disponible()])
                return JsonResponse({'result': 'ok', 'lista': lista,'lista1':lista1})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', "mensaje": u"Error al actualizar costo. %s"%ex})

        elif action == 'cambiar_valor_stockcomprometido':
            try:
                stock1 = ItemUnidadMedidaStock.objects.get(pk=int(request.POST['id']))
                stockcomprometido = Decimal(request.POST['stockcomprometido'])
                stock1.stockcomprometido = stockcomprometido
                stock1.save(request)
                return JsonResponse({'result': 'ok', 'stockcomprometido': stock1.stockcomprometido,'stock_disponible':stock1.stock_disponible()})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', "mensaje": u"Error al actualizar stock comprometido."})

        elif action == 'detalles':
            try:
                from django.db.models import F
                item = Item.objects.get(pk=encrypt(request.POST['iddet']))
                equivalencias = ItemUnidadMedidaEquivalencia.objects.filter(status=True, itemunidadmedida__item=item, itemunidadmedida__item__status=True).exclude(unidad_medida_origen=F('unidad_medida_fin')).order_by('-orden')
                # ofertas = OfertaItem.objects.filter(status=True,itemunidadmedida=stock.itemunidadmedida)
                template = get_template("view_stock/detalles.html")
                json_content = template.render({'equivalencias': equivalencias})
                return JsonResponse({"result": "ok", 'html': json_content})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'ofertas':
            try:
                from django.db.models import F
                itemumstock = ItemUnidadMedidaStock.objects.get(pk=encrypt(request.POST['iddet']))
                ofertas = OfertaItem.objects.filter(status=True,itemunidadmedida=itemumstock.itemunidadmedida)
                template = get_template("view_stock/ofertas.html")
                json_content = template.render({'ofertas': ofertas})
                return JsonResponse({"result": "ok", 'html': json_content})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})


        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['titulo'] = u'Adicionar Proveedor'
                    form = ProveedorForm()
                    data['form'] = form
                    return render(request, "gest_proveedor/add.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(request.path)

        else:
            try:
                data['title'] = u'Existencias de Productos'
                sucursal_select = 0
                producto_select = 0
                data['productos'] =None
                eItemUnidadMedidaStock= ItemUnidadMedidaStock.objects.filter(status=True,itemunidadmedida__item__status=True).distinct('itemunidadmedida__item','sucursal')
                data['sucursaleStock'] = Sucursal.objects.filter(status=True, id__in=eItemUnidadMedidaStock.values_list('sucursal_id', flat=True))
                data['productoStock'] = Item.objects.filter(status=True, id__in=eItemUnidadMedidaStock.values_list('itemunidadmedida__item_id', flat=True))
                if 'sucursal' in request.GET:
                    if request.GET['sucursal']:
                        sucursal_select= int(request.GET['sucursal'])
                        if sucursal_select >0:
                            eItemUnidadMedidaStock = eItemUnidadMedidaStock.filter(sucursal_id=sucursal_select)
                            data['productos'] = Item.objects.filter(status=True,
                                                                    id__in=eItemUnidadMedidaStock.values_list(
                                                                        'itemunidadmedida__item_id',
                                                                        flat=True))
                if 'producto' in request.GET:
                    if request.GET['producto']:
                        producto_select= int(request.GET['producto'])
                        if producto_select >0:
                            eItemUnidadMedidaStock = eItemUnidadMedidaStock.filter(itemunidadmedida__item_id=producto_select)
                if sucursal_select ==0 and producto_select==0:
                    eItemUnidadMedidaStock=None
                data['existencias'] = eItemUnidadMedidaStock
                data['producto_select'] = producto_select
                data['sucursal_select'] = sucursal_select
                return render(request, "view_stock/view.html", data)
            except Exception as ex:
                pass
