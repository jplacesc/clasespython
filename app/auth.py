from django.db import transaction
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from app.models import *
from django.core.exceptions import ObjectDoesNotExist
from app.funciones import *
__author__ = 'Jussy'
unicode = str
@transaction.atomic()
def login_user(request):
    from app.models import Cliente, Vendedor
    data = {}
    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']
            if action == 'login':
                try:
                    user = authenticate(username=request.POST['usuario'].lower(), password=request.POST['clave'])
                    if user is not None:
                        if not user.is_active:
                            log(u'Login fallido, usuario inactivo: %s' % (request.POST['usuario']), request, "add")
                            return HttpResponse(
                                json.dumps({"result": "bad", "mensaje": 'Login fallido, usuario inactivo.'}),
                                content_type="application/json")
                        else:
                            login(request, user)
                            request.session['autenticado'] = True
                            request.session['usuario'] = user
                            sucursales = None
                            request.session['sucursalsesion'] = None
                            request.session['ultimo_acceso'] = datetime.now()
                            if user.is_superuser:
                                if Sucursal.objects.values('id').filter(status=True,tipo=2).exists():
                                    sucursales = Sucursal.objects.filter(status=True,tipo=2)
                                if Vendedor.objects.filter(usuario=user, status=True).exists():
                                    vendedor = Vendedor.objects.filter(usuario=user, status=True)[0]
                                    request.session['vendedor'] = vendedor
                                    if vendedor.obtener_sucursal():
                                        sucursalesaux = sucursales.filter(id=vendedor.obtener_sucursal().sucursal_id)
                                        request.session['sucursalsesion'] = sucursalesaux[0]
                                else:
                                    request.session['sucursalsesion'] = sucursales[0]
                            elif Vendedor.objects.filter(usuario=user, status=True).exists():
                                vendedor = Vendedor.objects.filter(usuario=user, status=True)[0]
                                request.session['vendedor'] = vendedor
                                if vendedor.obtener_sucursal():
                                    sucursales = Sucursal.objects.filter(id=vendedor.obtener_sucursal().sucursal_id)
                                    request.session['sucursalsesion'] = sucursales[0]
                                else:
                                    request.session['sucursalsesion'] = None
                            log(u'Login con exito: %s ' % (user.username), request, "add")
                            return HttpResponse(json.dumps({"result": "ok","sessionid": request.session.session_key}), content_type="application/json")
                    log(u'Login fallido, no existe el usuario: %s' % (request.POST['usuario']), request, "add")
                    return HttpResponse(
                        json.dumps({"result": "bad", "mensaje": 'Login fallido, usuario o clave incorrecta.'}),
                        content_type="application/json")
                except Exception as ex:
                    return HttpResponse(
                        json.dumps({"result": "bad", "mensaje": 'Login fallido, Error en el sistema. '}),
                        content_type="application/json")

        return HttpResponse(json.dumps({"result": "bad", "mensaje": "Solicitud Incorrecta."}),
                            content_type="application/json")

    else:
        if 'autenticado' in request.session:
            return HttpResponseRedirect("/")
        data['request'] = request
        return render(request, "login.html", data)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/login")


@login_required(redirect_field_name='ret', login_url='/login')
@transaction.atomic()
def panel(request):
    data = {}
    data['hoy'] = datetime.now()
    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']

        return HttpResponse(json.dumps({"result": "bad", "mensaje": 'Solicitud Incorrecta.'}),
                            content_type="application/json")
    else:
        hoy = datetime.now()
        data['title'] = 'Menú Principal'
        if 'action' in request.GET:
            action = request.GET['action']
            return HttpResponseRedirect(request.path)
        else:
            try:
                data['titulo'] = 'Menú Principal'
                data['usuario'] = usuario = request.session['usuario']
                sucursales = None
                modulos = None
                if Sucursal.objects.values('id').filter(status=True,tipo=2).exists():
                    sucursales = Sucursal.objects.filter(status=True,tipo=2)
                if 'vendedor' in request.session:
                    vendedor = request.session['vendedor']
                modulos = Modulo.objects.filter(status=True, activo=True)
                if CambioClaveUsuario.objects.values("id").filter(status=True, usuario=usuario).exists():
                    return HttpResponseRedirect('/cambioclave')
                data['sucursales'] = sucursales
                data['modulos'] = modulos
                return render(request, "index.html", data)
            except Exception as ex:
                return HttpResponseRedirect('/logout')

@login_required(redirect_field_name='ret', login_url='/login')
@transaction.atomic()
def cambiarsucursal(request):
    try:
        data = {}
        sucursal = Sucursal.objects.get(pk=request.GET['id'])
        request.session['sucursalsesion'] = sucursal
        carga_plantilla_base(request, data)
        return JsonResponse({"result": "ok"})
    except Exception as ex:
        transaction.set_rollback(True)
        return HttpResponseRedirect('/logout')

