# coding=utf-8
import os
import io as StringIO

from app.settings import *
from django.template.loader import get_template
from django.template import Context
from xhtml2pdf import pisa
from django.http import HttpResponse, JsonResponse

def link_callback(uri, rel):
    sUrl = STATIC_URL      # Typically /static/
    sRoot = STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = MEDIA_URL       # Typically /static/media/
    mRoot = MEDIA_ROOT     # Typically /home/userX/project_static/media/

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri                  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))

    return path


def conviert_html_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict).encode(encoding="UTF-8")
    result = StringIO.BytesIO()
    pisaStatus = pisa.CreatePDF(StringIO.BytesIO(html), result, link_callback=link_callback)
    if not pisaStatus.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return JsonResponse({"result": "bad", "mensaje": u"Problemas al ejecutar el reporte."})


def conviert_html_to_pdfsave(template_src, context_dict, filename):
    template = get_template(template_src)
    html = template.render(context_dict).encode(encoding="UTF-8")
    result = StringIO.BytesIO()
    output_folder = os.path.join(SITE_STORAGE, 'media', 'qrcode', 'evaluaciondocente')
    filepdf = open(output_folder + os.sep + filename, "w+b")
    links = lambda uri, rel: os.path.join(MEDIA_ROOT, uri.replace(MEDIA_URL, ''))
    pdf1 = pisa.pisaDocument(StringIO.BytesIO(html), dest=filepdf, link_callback=links)
    pisaStatus = pisa.CreatePDF(StringIO.BytesIO(html), result, link_callback=links)
    if not pdf1.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return JsonResponse({"result": "bad", "mensaje": u"Problemas al ejecutar el reporte."})


