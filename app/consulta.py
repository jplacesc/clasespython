# -*- coding: latin-1 -*-
from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.db import transaction
from django.http import JsonResponse
from app.models import Pais,Provincia,Ciudad
unicode = str
from django.db.models import Q

@transaction.atomic()
def view(request):
    if request.method == 'POST':
        if 'a' in request.POST:
            action = request.POST['a']


            if action == 'provincias':
                try:
                    pais = Pais.objects.get(pk=request.POST['id'])
                    lista = []
                    for provincia in pais.provincia_set.all():
                        lista.append([provincia.id, provincia.nombre])
                    return JsonResponse({'result': 'ok', 'lista': lista})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})

            elif action == 'ciudades':
                try:
                    provincia = Provincia.objects.get(pk=request.POST['id'])
                    lista = []
                    for ciudad in provincia.ciudad_set.all():
                        lista.append([ciudad.id, ciudad.nombre])
                    return JsonResponse({'result': 'ok', 'lista': lista})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al obtener los datos."})


            elif action == 'logout':
                try:
                    if 'tiposistema' in request.session:
                        urlreturn = '/login'
                        logout(request)
                        return JsonResponse({'result': 'ok', 'url': urlreturn})
                    else:
                        logout(request)
                        return JsonResponse({'result': 'ok', 'url': '/login'})
                except Exception as ex:
                    return JsonResponse({"result": "bad", "mensaje": u"Error al cerrar session."})


        return JsonResponse(['clases', 'Jussy Design'])
    else:
        if 'a' in request.GET:
            action = request.GET['a']


        return JsonResponse(['Jussy Design', '(C) Todos los derechos reservados'])