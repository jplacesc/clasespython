# -*- coding: UTF-8 -*-
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.encoding import force_str

from app.formularios import *
from django.db import connection, transaction
from django.template import Context
import sys
from django.template.loader import get_template
from app.funciones import log, cargar_plantilla_base_simple, MiPaginador
from django.shortcuts import render, redirect

@login_required(redirect_field_name='ret', login_url='/loginsga')
@transaction.atomic()
def view(request):
    data = {}
    cargar_plantilla_base_simple(request,data)
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'agregarVendedor':
            try:
                with transaction.atomic():
                    form = VendedorForm(request.POST)
                    if form.is_valid():
                        if User.objects.values('id').filter(username=form.cleaned_data['username'].strip()).exists():
                            raise NameError(u"Ya existe un usuario con ese nombre de usuario.")
                        if Vendedor.objects.values('id').filter(identificacion=form.cleaned_data['identificacion'].strip()).exists():
                            raise NameError(u"Ya existe un vendedor con la misma identificación.")
                        user = User.objects.create_user(form.cleaned_data['username'],
                                                        form.cleaned_data['email'],
                                                        form.cleaned_data['password'],
                                                        first_name = form.cleaned_data['nombre'],
                                                        last_name = form.cleaned_data['apellido'])
                        user.save()
                        vendedor = Vendedor(identificacion=form.cleaned_data['identificacion'],
                                            nombre=form.cleaned_data['nombre'],
                                            apellido=form.cleaned_data['apellido'],
                                            nacimiento=form.cleaned_data['nacimiento'],
                                            sexo=form.cleaned_data['sexo'],
                                            email=form.cleaned_data['email'],
                                            pais=form.cleaned_data['pais'],
                                            provincia=form.cleaned_data['provincia'],
                                            ciudad=form.cleaned_data['ciudad'],
                                            direccion=form.cleaned_data['direccion'],
                                            celular=form.cleaned_data['celular'],
                                            usuario=user,
                                            )
                        vendedor.save(request)
                        cambioclave = vendedor.cambiar_clave()
                        cambioclave.solicitada = True
                        cambioclave.clavecambio = form.cleaned_data['password']
                        cambioclave.save(request)

                        if not SucursalVendedor.objects.values('id').filter(vendedor=vendedor, sucursal=form.cleaned_data['sucursal']).exists():
                            sucursalvendedor = SucursalVendedor(sucursal=form.cleaned_data['sucursal'],
                                                                vendedor=vendedor)
                            sucursalvendedor.save(request)
                        messages.success(request, 'Registro guardado con éxito.')
                        res_json ={"result": False}
                    else:
                        res_json = {'result': True, "mensaje": "Error en el formulario: {}".format([{k: v[0]} for k, v in form.errors.items()])}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'result': True, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'editarVendedor':
            try:
                with transaction.atomic():
                    vendedor = Vendedor.objects.get(pk=request.POST['id'])
                    form = VendedorForm(request.POST)
                    if form.is_valid():
                        vendedor.nombre = form.cleaned_data['nombre']
                        vendedor.apellido = form.cleaned_data['apellido']
                        vendedor.nacimiento = form.cleaned_data['nacimiento']
                        vendedor.sexo = form.cleaned_data['sexo']
                        vendedor.email = form.cleaned_data['email']
                        vendedor.pais = form.cleaned_data['pais']
                        vendedor.provincia = form.cleaned_data['provincia']
                        vendedor.ciudad = form.cleaned_data['ciudad']
                        vendedor.direccion = form.cleaned_data['direccion']
                        vendedor.celular = form.cleaned_data['celular']
                        vendedor.save(request)
                        messages.success(request, 'Registro guardado con éxito.')
                        res_json = {"result": False}
                    else:
                        res_json = {'result': True, "mensaje": "Error en el formulario: {}".format([{k: v[0]} for k, v in form.errors.items()])}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'result': True, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'eliminarVendedor':
            try:
                if not 'id' in request.POST or not request.POST['id']:
                    raise NameError(u"No se encontro registro a eliminar")
                object_id = int(request.POST['id'])
                if not Vendedor.objects.filter(pk=object_id).exists():
                    raise NameError(u"No se encontro registro a eliminar")
                eVendedor = Vendedor.objects.get(pk=object_id)
                eVendedor.delete()
                messages.success(request, 'Registro eliminado con éxito.')
                res_json = {"result": False}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'result': True, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'consulta_usuario':
            try:
                if User.objects.filter(username=request.GET['username']).exists():
                    raise NameError(u"El nombre de usuario ya existe")
                else:
                    res_json = {"result": False}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'result': True, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'detallesucursal':
            try:
                vendedor = Vendedor.objects.get(pk=request.POST['id'])
                template = get_template("vendedor/detallesucursal.html")
                json_content = template.render({'vendedor': vendedor})
                return JsonResponse({"result": "ok", 'html': json_content})
            except Exception as ex:
                return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

        return JsonResponse({"result": True, "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'agregarVendedor':
                try:
                    form = VendedorForm()
                    data['action'] = 'agregarVendedor'
                    data['form'] = form
                    template = get_template("vendedor/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass


            elif action == 'editarVendedor':
                try:
                    data['id'] = request.GET['id']
                    data['action'] = 'editarVendedor'
                    data['filtro'] = vendedorc = Vendedor.objects.get(pk=request.GET['id'])
                    initial = model_to_dict(vendedorc)
                    form = VendedorForm(initial=initial)
                    form.editar()
                    data['form'] = form
                    template = get_template("vendedor/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            return HttpResponseRedirect(request.path)
        else:
            try:
                data['title'] = 'Administración de Vendedores'
                filtros,s, url_vars, id = Q(), request.GET.get('s', ''),'', request.GET.get('id', '0')
                eVendedor = Vendedor.objects.filter(status=True)
                if int(id):
                    filtros = filtros & (Q(id=id))
                    data['id'] = f"{id}"
                    url_vars += f"&id={id}"
                if s:
                    filtros = filtros & (Q(nombre__icontains=s)|Q(apellido__icontains=s))
                    data['s'] = f"{s}"
                    url_vars += f"&s={s}"
                if filtros:
                    eVendedor = eVendedor.filter(filtros).order_by('apellido')
                paging = MiPaginador(eVendedor, 15)
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
                data['vendedores'] = page.object_list
                data['url_vars'] = url_vars
                return render(request, "vendedor/view.html", data)
            except Exception as ex:
                pass
