# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import login_required
from app.models import *
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from datetime import datetime
# from app.auth import adduserdata
from django.db import transaction

@login_required(redirect_field_name='', login_url='/login')
# @secure_module
# @last_access
@transaction.atomic()
def view(request):
    data = {}
    data['currenttime'] = datetime.now()
    persona = request.session['persona']
    # adduserdata(request, data)

    if request.method == 'POST':
        action = request.POST['action']
        return JsonResponse({"result": "bad", "mensaje": u"Solicitud Incorrecta."})
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            return HttpResponseRedirect(request.path)
        else:
            try:
                data['title'] = 'UXplora'
                return render(request, "panelnew.html", data)
            except Exception as ex:
                import sys
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
                return HttpResponseRedirect('/logout')