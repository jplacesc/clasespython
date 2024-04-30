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
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.encoding import force_str
from app.formularios import *
from django.db import connection, transaction
from django.template import Context
import sys
from django.template.loader import get_template
from app.funciones import log,  cargar_plantilla_base_simple, MiPaginador
from django.shortcuts import render, redirect

@login_required(redirect_field_name='ret', login_url='/loginsga')
@transaction.atomic()
def view(request):
    data = {}
    cargar_plantilla_base_simple(request,data)
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'agregarGrupo':
            try:
                with transaction.atomic():
                    form = GrupoForm(request.POST)
                    if form.is_valid():
                        if not request.user.has_perm('app.puede_agregar_grupo'):
                            raise NameError(u'Lo sentimos, Ud no puede agregar grupos.')
                        if not Group.objects.values('id').filter(name=form.cleaned_data['name']).exists():
                            instance = Group(name=form.cleaned_data['name'])
                            instance.save(request)
                            messages.success(request, 'Registro guardado con éxito.')
                            return JsonResponse({"result": False}, safe=False)
                        else:
                            raise NameError(u'El registro ya existe.')
                    else:
                        return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in form.errors.items()], "mensaje": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": True, "mensaje": '%s' % ex}, safe=False)

        elif action == 'editarGrupo':
            try:
                with transaction.atomic():
                    filtro = Group.objects.get(pk=request.POST['id'])
                    form = GrupoForm(request.POST)
                    if form.is_valid():
                        if not Group.objects.values('id').filter(name=form.cleaned_data['name']).exclude(pk=filtro.id).exists():
                            filtro.name = form.cleaned_data['name']
                            filtro.save()
                            messages.success(request, 'Registro editado con éxito.')
                            return JsonResponse({"result": False}, safe=False)
                        else:
                            raise NameError(u'Ya existe un registro con el nombre: %s.'%form.cleaned_data['name'])
                    else:
                        return JsonResponse({'result': True, "form": [{k: v[0]} for k, v in form.errors.items()], "message": "Error en el formulario"})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": True, "mensaje": '%s' % ex}, safe=False)

        elif action == 'eliminarGrupo':
            try:
                if not 'id' in request.POST or not request.POST['id']:
                    raise NameError(u"No se encontro registro a eliminar")
                object_id = int(request.POST['id'])
                if not Group.objects.filter(pk=object_id).exists():
                    raise NameError(u"No se encontro registro a eliminar")
                eGroup = Group.objects.get(pk=object_id)
                eGroup.delete()
                messages.success(request, 'Registro eliminado con éxito.')
                res_json = {"error": False}
            except Exception as ex:
                transaction.set_rollback(True)
                res_json = {'error': True, "message": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        elif action == 'addgrupo':
            try:
                f = GrupoForm(request.POST)
                if f.is_valid():
                    grupo = Group(name=f.cleaned_data['name'])
                    grupo.save(request)
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        elif action == 'editgrupo':
            try:
                f = GrupoForm(request.POST)
                if f.is_valid():
                    grupo = Group.objects.get(pk=request.POST['id'])
                    grupo.name = f.cleaned_data['name']
                    grupo.save()
                    return JsonResponse({"result": "ok"})
                else:
                    raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": "bad", "mensaje": u"Error al guardar los datos."})

        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'agregarGrupo':
                try:
                    form = GrupoForm()
                    data['action'] = 'agregarGrupo'
                    data['form'] = form
                    template = get_template("grupos/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass


            elif action == 'editarGrupo':
                try:
                    data['id'] = request.GET['id']
                    data['action'] = 'editarGrupo'
                    data['filtro'] = grupo = Group.objects.get(pk=request.GET['id'])

                    form = GrupoForm(initial={'name': grupo.name})
                    data['form'] = form
                    template = get_template("grupos/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass

            elif action == 'addgrupo':
                try:
                    data['title'] = u'Adicionar Grupo'
                    data['form'] = GrupoForm()
                    return render(request, 'grupos/addgrupo.html', data)
                except Exception as ex:
                    pass

            elif action == 'editgrupo':
                try:
                    data['title'] = u'Editar Grupo'
                    data['grupo'] = grupo = Group.objects.get(pk=request.GET['id'])
                    form = GrupoForm(initial={'name': grupo.name})
                    data['form'] = form
                    return render(request, "grupos/editgrupo.html", data)
                except Exception as ex:
                    pass
            return HttpResponseRedirect(request.path)
        else:
            try:
                data['title'] = 'Administración de Grupos del Sistema'
                filtros,s, url_vars, id = Q(), request.GET.get('s', ''),'', request.GET.get('id', '0')
                eGrupos = Group.objects.all()
                if int(id):
                    filtros = filtros & (Q(id=id))
                    data['id'] = f"{id}"
                    url_vars += f"&id={id}"
                if s:
                    filtros = filtros & (Q(name__icontains=s))
                    data['s'] = f"{s}"
                    url_vars += f"&s={s}"
                if filtros:
                    eGrupos = eGrupos.filter(filtros).order_by('name')
                paging = MiPaginador(eGrupos, 15)
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
                data['eGrupos'] = page.object_list
                data['url_vars'] = url_vars
                return render(request, "grupos/view.html", data)
            except Exception as ex:
                pass
