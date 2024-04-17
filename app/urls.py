from app import settings,auth
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.urls import re_path
from app import grupos,vendedor,consulta,producto,view_stock,facturacion
urlpatterns = [
    path('', auth.panel, name='principal'),
    path('login', auth.login_user, name='Loginuser'),
    path('logout', auth.logout_user, name='Logoutuser'),
    path('admin/', admin.site.urls),
    path('grupos', grupos.view, name='grupos'),
    path('vendedor', vendedor.view, name='vendedor'),
    path('consulta', consulta.view, name='consulta'),
    path('producto', producto.view, name='producto'),
    path('view_stock', view_stock.view, name='producto'),
    path('facturacion', facturacion.view, name='facturacion')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)