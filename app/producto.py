# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from app.formularios import ItemForm,ItemUnidadMedidaForm
from app.funciones import log, cargar_plantilla_base_simple, MiPaginador
from app.models import Item, ItemUnidadMedida, Impuesto, ItemUnidadMedidaEquivalencia, Marca,UnidadMedida,ItemCategoria
from datetime import datetime
from django.db.models import Max
from django.template.loader import get_template
from django.db.models import Q
from django.contrib import messages
@login_required(redirect_field_name='ret', login_url='/login')
# @secure_module
# @last_access
@transaction.atomic()
def view(request):
    data = {}
    data['usuario'] = usuario = request.session['usuario']
    cargar_plantilla_base_simple(request, data)
    hoy = datetime.now().date()
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'agregarProducto':
            try:
                form = ItemForm(request.POST)
                if form.is_valid():
                    if Item.objects.values('id').filter(status=True,codigo=form.cleaned_data['codigo'],categoria=form.cleaned_data['categoria']).exists():
                        raise NameError(u"El código de item ya existe..")

                    item = Item(codigo=form.cleaned_data['codigo'],
                                descripcion=form.cleaned_data['descripcion'],
                                categoria=form.cleaned_data['categoria'],
                                marca=form.cleaned_data['marca'],
                                unidad_base=form.cleaned_data['unidad_base'],
                                impuesto=form.cleaned_data['impuesto'],
                                )
                    item.save(request)
                    messages.success(request, 'Registro guardado con éxito.')
                    res_json = {"result": False}
                else:
                    res_json = {'result': True, "mensaje": "Error en el formulario: {}".format([{k: v[0]} for k, v in form.errors.items()])}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'result': True, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'editarProducto':
            try:
                item = Item.objects.get(pk=request.POST['id'])
                form = ItemForm(request.POST)
                if form.is_valid():
                    if Item.objects.values('id').filter(status=True, codigo=form.cleaned_data['codigo'], categoria=form.cleaned_data['categoria']).exists() and not item.codigo==form.cleaned_data['codigo']:
                        raise NameError(u"El código de item ya existe.")
                    item.codigo = form.cleaned_data['codigo']
                    item.descripcion = form.cleaned_data['descripcion']
                    item.categoria = form.cleaned_data['categoria']
                    item.marca = form.cleaned_data['marca']
                    item.unidad_base = form.cleaned_data['unidad_base']
                    item.impuesto = form.cleaned_data['impuesto']
                    item.save(request)
                    messages.success(request, 'Registro guardado con éxito.')
                    res_json = {"result": False}
                else:
                    res_json = {'result': True, "mensaje": "Error en el formulario: {}".format(
                        [{k: v[0]} for k, v in form.errors.items()])}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'result': True, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'eliminarProducto':
            try:
                item = Item.objects.get(pk=request.POST['id'])
                item.status = False
                item.save(request)
                messages.success(request, 'Registro eliminado con éxito.')
                res_json = {"result": False}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'result': True, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'agregarItemUnidadMedida':
            try:
                form = ItemUnidadMedidaForm(request.POST)
                if form.is_valid():
                    item = Item.objects.get(id=request.POST['id'])
                    if item.itemunidadmedida_set.filter(status=True, orden=form.cleaned_data['orden']).exists():
                        raise NameError(u"El orden ya existe.")
                    itemunidad = ItemUnidadMedida(item=item, unidad_medida=form.cleaned_data['unidad_medida'],
                        porcentaje_ganancia=form.cleaned_data['porcentaje_ganancia'], orden=form.cleaned_data['orden'])
                    itemunidad.save(request)
                    if not ItemUnidadMedidaEquivalencia.objects.filter(status=True, valorumorigen=1,
                                                                     equivalenciaumfin__gte=1,
                                                                     unidad_medida_origen=itemunidad.unidad_medida,
                                                                     unidad_medida_fin=itemunidad.unidad_medida).exists():
                        equivalencia = ItemUnidadMedidaEquivalencia(itemunidadmedida=itemunidad,
                                                                    valorumorigen=1,
                                                                    unidad_medida_origen=itemunidad.unidad_medida,
                                                                    equivalenciaumfin=1,
                                                                    unidad_medida_fin=itemunidad.unidad_medida,
                                                                    orden=form.cleaned_data['orden']
                                                                    )
                        equivalencia.save()

                    messages.success(request, 'Registro guardado con éxito.')
                    res_json = {"result": False}
                else:
                    res_json = {'result': True, "mensaje": "Error en el formulario: {}".format([{k: v[0]} for k, v in form.errors.items()])}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'result': True, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'editarItemUnidadMedida':
            try:
                itemunidad = ItemUnidadMedida.objects.get(pk=request.POST['id'])
                form = ItemUnidadMedidaForm(request.POST)
                if form.is_valid():
                    if itemunidad.orden != form.cleaned_data['orden']:
                        if ItemUnidadMedida.objects.values('id').filter(status=True, item=itemunidad.item,orden=form.cleaned_data['orden']).exists():
                            raise NameError(u"El orden ya existe.")
                    itemunidad.porcentaje_ganancia = form.cleaned_data['porcentaje_ganancia']
                    itemunidad.unidad_medida = form.cleaned_data['unidad_medida']
                    itemunidad.orden = form.cleaned_data['orden']
                    itemunidad.save(request)

                    if not ItemUnidadMedidaEquivalencia.objects.filter(status=True, valorumorigen=1,
                                                                     equivalenciaumfin__gte=1,
                                                                     unidad_medida_origen=itemunidad.unidad_medida,
                                                                     unidad_medida_fin=itemunidad.unidad_medida).exists():
                        equivalencia = ItemUnidadMedidaEquivalencia(itemunidadmedida=itemunidad,
                                                                    valorumorigen=1,
                                                                    unidad_medida_origen=itemunidad.unidad_medida,
                                                                    equivalenciaumfin=1,
                                                                    unidad_medida_fin=itemunidad.unidad_medida,
                                                                    orden=form.cleaned_data['orden']
                                                                    )
                        equivalencia.save()
                    else:
                        equivalencia = ItemUnidadMedidaEquivalencia.objects.filter(status=True, valorumorigen=1,
                                                                    equivalenciaumfin__gte=1,
                                                                    unidad_medida_origen=itemunidad.unidad_medida,
                                                                    unidad_medida_fin=itemunidad.unidad_medida)[0]
                        equivalencia.orden=form.cleaned_data['orden']
                        equivalencia.save(request)
                    messages.success(request, 'Registro guardado con éxito.')
                    res_json = {"result": False}
                else:
                    res_json = {'result': True, "mensaje": "Error en el formulario: {}".format([{k: v[0]} for k, v in form.errors.items()])}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'result': True, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'eliminarItemUnidadMedida':
            try:
                if not 'id' in request.POST or not request.POST['id']:
                    raise NameError(u"No se encontro registro a eliminar")
                eItemUnidadMedida = ItemUnidadMedida.objects.get(pk=request.POST['id'])
                if not eItemUnidadMedida.en_uso():
                    eItemUnidadMedida.status=False
                    eItemUnidadMedida.save(request)
                    ItemUnidadMedidaEquivalencia.objects.filter(status=True, itemunidadmedida=eItemUnidadMedida).update(status=False)
                    return JsonResponse({"result": "ok"})
                else:
                    return JsonResponse({"result": "bad", "mensaje": u"La unidad de medida no puede ser eliminada."})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al eliminar los datos."})

        elif action == 'addequivalencia':
            try:
                f = ItemUnidadMedidaEquivalenciaForm(request.POST)
                if f.is_valid():
                    equivalencia = ItemUnidadMedidaEquivalencia(
                        itemunidadmedida_id=int(request.POST['itemunidadmedida']),
                        valorumorigen=1,
                        unidad_medida_origen=f.cleaned_data['unidad_medida_origen'],
                        equivalenciaumfin=f.cleaned_data['equivalenciaumfin'],
                        unidad_medida_fin=f.cleaned_data['unidad_medida_fin'])
                    equivalencia.save(request)
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'cambiarequivalenciaumfin':
            try:
                equivalencia = ItemUnidadMedidaEquivalencia.objects.get(pk=int(request.POST['idi']))
                valor = request.POST['valor']
                equivalencia.equivalenciaumfin = int(valor)
                equivalencia.save(request)
                return JsonResponse({'result': 'ok', 'valor': equivalencia.equivalenciaumfin})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': 'bad', "mensaje": u"Error al actualizar equivalencia."})

        elif action == 'eliminarEquivalencia':
            try:
                equivalencia = ItemUnidadMedidaEquivalencia.objects.get(pk=request.POST['id'])
                opc=0
                if equivalencia.status==True:
                    equivalencia.status=False
                else:
                    equivalencia.status=True
                    opc=1
                equivalencia.save(request)
                return JsonResponse({"result": "ok", "valor": opc})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al eliminar los datos."})

        elif action == 'consulta_marca':
            try:
                lista = []
                if Marca.objects.values('id').filter(status=True).distinct():
                    for marca in Marca.objects.filter(status=True).distinct():
                        lista.append([marca.id, marca.descripcion])
                return JsonResponse({'result': 'ok', 'lista': lista})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'consulta_unidad_base':
            try:
                lista = []
                if UnidadMedida.objects.values('id').filter(status=True).distinct():
                    for u in UnidadMedida.objects.filter(status=True).distinct():
                        lista.append([u.id, u'%s (%s)' % (u.descripcion, u.simbolo)])
                return JsonResponse({'result': 'ok', 'lista': lista})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'consulta_impuesto':
            try:
                lista = []
                if Impuesto.objects.values('id').filter(status=True).distinct():
                    for i in Impuesto.objects.filter(status=True).distinct():
                        lista.append([i.id, u'%s - %s' % (i.descripcion, i.valor)])
                return JsonResponse({'result': 'ok', 'lista': lista})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        elif action == 'consulta_categoria':
            try:
                lista = []
                if ItemCategoria.objects.values('id').filter(status=True).distinct():
                    for i in ItemCategoria.objects.filter(status=True).distinct():
                        lista.append([i.id, u'%s' % (i.descripcion)])
                return JsonResponse({'result': 'ok', 'lista': lista})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'agregarProducto':
                try:
                    data['action'] = 'agregarProducto'
                    eImpuesto=Impuesto.objects.filter(status=True, fechainicio__lte=hoy, fechafin__gte=hoy)
                    form = ItemForm(initial={'impuesto':eImpuesto.valor if eImpuesto else ''})
                    data['form'] = form
                    template = get_template("producto/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'editarProducto':
                try:
                    data['id'] = request.GET['id']
                    data['action'] = 'editarProducto'
                    data['item'] = item = Item.objects.get(status=True, pk=request.GET['id'])
                    initial = model_to_dict(item)
                    form = ItemForm(initial=initial)
                    data['form'] = form
                    template = get_template("producto/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'agregarItemUnidadMedida':
                try:
                    data['item'] = item = Item.objects.get(status=True, pk=request.GET['id'])
                    data['id'] = request.GET['id']
                    data['action'] = u'agregarItemUnidadMedida'
                    orden = 1
                    ids = []
                    if item.itemunidadmedida_set.filter(status=True).exists():
                        orden = (item.itemunidadmedida_set.filter(status=True).aggregate(orden=Max('orden'))['orden']) + 1
                        ids = item.itemunidadmedida_set.values_list('unidad_medida', flat=True).filter(status=True)
                    form = ItemUnidadMedidaForm(initial={'orden': orden, 'unidad_medida': item })
                    form.excluirUnidadesUsadas(ids)
                    data['form'] = form
                    template = get_template("producto/formItemUnidad.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'editarItemUnidadMedida':
                try:
                    data['itemunidad'] = itemunidad = ItemUnidadMedida.objects.get(status=True, pk=request.GET['id'])
                    data['id'] = request.GET['id']
                    data['action'] = u'editarItemUnidadMedida'
                    ids = ItemUnidadMedida.objects.values_list('unidad_medida', flat=True).filter(status=True,item=itemunidad.item).exclude(unidad_medida=itemunidad.unidad_medida)
                    initial = model_to_dict(itemunidad)
                    form = ItemUnidadMedidaForm(initial=initial)
                    form.excluirUnidadesUsadas(ids)
                    data['form'] = form
                    template = get_template("producto/formItemUnidad.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'itemUnidadMedida':
                try:
                    data['item'] = item = Item.objects.get(pk=request.GET['id'])
                    data['title'] = u'Asignación de Unidades de Medida por item'
                    filtros, s, url_vars, id = Q(), request.GET.get('s', ''), '', request.GET.get('id', '0')
                    eItemUnidadMedida = ItemUnidadMedida.objects.filter(status=True, item=item).order_by('orden')
                    if s:
                        filtros = filtros & (Q(unidad_medida__descripcion__icontains=s) | Q(unidad_medida__simbolo__icontains=s))
                        data['s'] = f"{s}"
                        url_vars += f"&s={s}"
                    if filtros:
                        eItemUnidadMedida = eItemUnidadMedida.filter(filtros).order_by('orden')
                    paging = MiPaginador(eItemUnidadMedida, 15)
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
                    data['itemunidadmedidas'] = page.object_list
                    data['url_vars'] = url_vars
                    return render(request, "producto/itemUnidadMedida.html", data)
                except Exception as ex:
                    pass

            elif action == 'equivalencias':
                try:
                    data['item'] = item = Item.objects.get(pk=request.GET['id'])
                    unidades = item.itemunidadmedida_set.filter(status=True).order_by('-orden')
                    data['title'] = u'Equivalencias de Items'
                    for x in unidades:
                        for m in item.itemunidadmedida_set.filter(status=True, orden__lte=(x.orden)).order_by('-orden'):
                            if not m.itemunidadmedidaequivalencia_set.filter(status=True, valorumorigen=1,
                                                                             equivalenciaumfin__gte=1,
                                                                             unidad_medida_origen=x.unidad_medida,
                                                                             unidad_medida_fin=m.unidad_medida).exists():
                                equivalencia = ItemUnidadMedidaEquivalencia(itemunidadmedida=m,
                                                                            valorumorigen=1,
                                                                            unidad_medida_origen=x.unidad_medida,
                                                                            equivalenciaumfin=5 if x.unidad_medida_id == 7 and m.unidad_medida_id == 13 else 1,
                                                                            unidad_medida_fin=m.unidad_medida,
                                                                            orden=x.orden
                                                                            )
                                equivalencia.save()
                    data['equivalencias'] = equivalencias = ItemUnidadMedidaEquivalencia.objects.filter(status=True,itemunidadmedida__item=item).order_by('-orden')
                    return render(request, "producto/equivalencias.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(request.path)

        else:
            try:
                data['title'] = 'Administración de productos'
                filtros,s, url_vars, id = Q(), request.GET.get('s', ''),'', request.GET.get('id', '0')
                eItems = Item.objects.filter(status=True)
                if int(id):
                    filtros = filtros & (Q(id=id))
                    data['id'] = f"{id}"
                    url_vars += f"&id={id}"
                if s:
                    filtros = filtros & (Q(descripcion__icontains=s)|Q(codigo__icontains=s))
                    data['s'] = f"{s}"
                    url_vars += f"&s={s}"
                if filtros:
                    eItems = eItems.filter(filtros).order_by('descripcion')
                paging = MiPaginador(eItems, 15)
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
                data['productos'] = page.object_list
                data['url_vars'] = url_vars
                return render(request, "producto/view.html", data)
            except Exception as ex:
                pass