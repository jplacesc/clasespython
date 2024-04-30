from app.funciones import ModeloBase
from django.db.models.query_utils import Q
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from django.db import models
from datetime import datetime, timedelta
from django.db.models import Sum

class Perms(models.Model):
    class Meta:
        permissions = (
            ("puede_agregar_grupo", "Puede agregar un grupo en el sistema"),
            ("puede_editar_grupo", "Puede editar grupo en el sistema"),
            ("puede_eliminar_grupo", "Puede eliminar grupo en el sistema"),
            ("puede_visualizar_unidad_medida", "Puede visualizar unidad de  medida"),
        )

class Sexo(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Sexo"
        verbose_name_plural = u"Sexos"
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Sexo, self).save(*args, **kwargs)

class Pais(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Nombre")

    @staticmethod
    def flexbox_query(q, extra=None):
        if extra:
            return eval('Pais.objects.filter(Q(nombre__contains="%s")).filter(%s).distinct()[:25]' % (q, extra))
        return Pais.objects.filter(Q(nombre__contains=q)).distinct()[:25]

    def flexbox_repr(self):
        return self.__str__()

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"País"
        verbose_name_plural = u"Paises"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def en_uso(self):
        return self.provincia_set.values('id').all().exists()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Pais, self).save(*args, **kwargs)

class Provincia(ModeloBase):
    pais = models.ForeignKey(Pais, blank=True, null=True, verbose_name=u'País', on_delete=models.CASCADE)
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Nombre")

    @staticmethod
    def flexbox_query(q, extra=None):
        if extra:
            return eval('Provincia.objects.filter(Q(nombre__contains="%s")).filter(%s).distinct()[:25]' % (q, extra))
        return Provincia.objects.filter(Q(nombre__contains=q)).distinct()[:25]

    def flexbox_repr(self):
        return self.__str__()

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Provincia"
        verbose_name_plural = u"Provincias"
        ordering = ['nombre']
        unique_together = ('nombre', 'pais')

    def en_uso(self):
        return self.ciudad_set.values('id').all().exists()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Provincia, self).save(*args, **kwargs)

class Ciudad(ModeloBase):
    provincia = models.ForeignKey(Provincia, blank=True, null=True, verbose_name=u'Provincia', on_delete=models.CASCADE)
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Nombre")

    @staticmethod
    def flexbox_query(q, extra=None):
        if extra:
            return eval('Canton.objects.filter(Q(nombre__contains="%s")).filter(%s).distinct()[:25]' % (q,extra))
        return Ciudad.objects.filter(Q(nombre__contains=q)).distinct()[:25]

    def flexbox_repr(self):
        return self.__str__()

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Canton"
        verbose_name_plural = u"Cantones"
        ordering = ['nombre']
        unique_together = ('nombre', 'provincia')


    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Ciudad, self).save(*args, **kwargs)
class CambioClaveUsuario(ModeloBase):
    usuario = models.ForeignKey(User, blank=True, null=True, verbose_name=u'Usuario', on_delete=models.SET_NULL)
    clavecambio = models.CharField(default='', max_length=50, verbose_name=u'Clave cambio')
    solicitada = models.BooleanField(default=False, verbose_name=u'Solicitada')

    class Meta:
        unique_together = ('usuario',)

class Modulo(ModeloBase):
    url = models.CharField(default='', max_length=100, verbose_name=u'URL')
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre')
    icono = models.CharField(default='', max_length=100, verbose_name=u'Icono')
    descripcion = models.CharField(default='', max_length=200, verbose_name=u'Descripción')
    visible = models.BooleanField(default=True, verbose_name=u'Visible')
    ordenmod = models.IntegerField(default=0, verbose_name=u'Orden')
    activo = models.BooleanField(default=True, verbose_name=u'Activo')

    def __str__(self):
        return u'%s (/%s)' % (self.nombre, self.url)

    class Meta:
        verbose_name = u"Modulo"
        verbose_name_plural = u"Modulos"
        ordering = ['ordenmod']
        unique_together = ('url',)

    def opciones(self):
        return self.opcionmodulo_set.filter(status=True, activo=True).order_by('orden')

    def misopciones(self, ids):
        return self.opcionmodulo_set.filter(status=True, activo=True, id__in=ids).order_by('orden')

    def save(self, *args, **kwargs):
        self.url = self.url.strip()
        self.nombre = self.nombre.strip().capitalize()
        self.icono = self.icono.strip()
        self.descripcion = self.descripcion.strip().capitalize()
        super(Modulo, self).save(*args, **kwargs)


class OpcionModulo(ModeloBase):
    modulo = models.ForeignKey(Modulo, verbose_name=u'Modulo', blank=True, null=True, on_delete=models.SET_NULL)
    url = models.CharField(default='', max_length=100, verbose_name=u'URL')
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre')
    icono = models.CharField(default='', max_length=100, verbose_name=u'Icono')
    descripcion = models.CharField(default='', max_length=200, verbose_name=u'Descripción')
    visible = models.BooleanField(default=True, verbose_name=u'Visible')
    orden = models.IntegerField(default=0, verbose_name=u'Orden')
    activo = models.BooleanField(default=True, verbose_name=u'Activo')

    def __str__(self):
        return u'%s (/%s)' % (self.nombre, self.url)

    class Meta:
        verbose_name = u"Opcion de modulo"
        verbose_name_plural = u"Opciones de modulos"
        ordering = ['orden']

    def save(self, *args, **kwargs):
        self.url = self.url.strip()
        self.nombre = self.nombre.strip().capitalize()
        self.icono = self.icono.strip()
        self.descripcion = self.descripcion.strip().capitalize()
        super(OpcionModulo, self).save(*args, **kwargs)


class ModuloGrupo(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u' Nombre')
    descripcion = models.CharField(default='', max_length=200, verbose_name=u'Descripción')
    opcion = models.ManyToManyField(OpcionModulo, verbose_name=u'Opcion de modulo')
    grupos = models.ManyToManyField(Group, verbose_name=u'Grupos')
    prioridad = models.IntegerField(default=0, verbose_name=u'Prioridad')

    def __str__(self):
        return u'%s - %s' % (self.nombre, self.descripcion)

    class Meta:
        verbose_name = u'Grupo de modulos'
        verbose_name_plural = u"Grupos de modulos"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def modulos_activos(self):
        return self.opcion.filter(activo=True)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip().capitalize()
        self.descripcion = self.descripcion.strip().capitalize()
        super(ModuloGrupo, self).save(*args, **kwargs)

class Cliente(ModeloBase):
    class TipoDocumento(models.IntegerChoices):
        NINGUNO = 0, "Ninguno"
        CEDULA = 1, "Cédula"
        PASAPORTE = 2, "Pasaporte"
        RUC = 3, "Ruc"

    tipodocumento = models.IntegerField(choices=TipoDocumento.choices, default=TipoDocumento.NINGUNO, blank=True, null=True,
                               verbose_name=u"Tipo Documento")
    identificacion = models.CharField(default='', max_length=20, blank=True, null=True, verbose_name=u"cedula")
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombres')
    apellido = models.CharField(default='', max_length=100, verbose_name=u"Apellidos")
    nacimiento = models.DateField(verbose_name=u"Fecha de Nacimiento", null=True, blank=True)
    sexo = models.ForeignKey(Sexo, default=2, verbose_name=u'Sexo', on_delete=models.CASCADE)
    email = models.CharField(default='', blank=True, null=True, max_length=200, verbose_name=u"Correo electronico personal")
    pais = models.ForeignKey(Pais, blank=True, null=True, verbose_name=u'País residencia', on_delete=models.SET_NULL)
    provincia = models.ForeignKey(Provincia, blank=True, null=True, verbose_name=u"Provincia de residencia", on_delete=models.SET_NULL)
    ciudad = models.ForeignKey(Ciudad, blank=True, null=True, verbose_name=u"Ciudad de residencia", on_delete=models.SET_NULL)
    direccion = models.CharField(default='', blank=True, null=True, max_length=100, verbose_name=u"Calle principal")
    celular = models.CharField(default='', max_length=50, verbose_name=u"Celular")
    usuario = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return u'%s %s' % (self.apellido, self.nombre)

    class Meta:
        verbose_name = u"Cliente"
        verbose_name_plural = u"Clientes"
        ordering = ['apellido', 'nombre']
        unique_together = ('identificacion',)

    @staticmethod
    def flexbox_query(q, extra=None):
        if extra:
            return eval('Cliente.objects.filter(Q(nombre__icontains="%s") | Q(apellido__icontains="%s") | Q(identificacion__icontains="%s"),status=True).filter(%s)' % (q, q, q, extra))
        return Cliente.objects.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(identificacion__icontains=q),status=True)

    def flexbox_repr(self):
        return str(self.nombre) + " - " + self.apellido + " - " + str(self.identificacion)

    def flexbox_alias(self):
        return [self.id, self.nombre, self.apellido]

    def direccion_completa(self):
        return u"%s %s %s" % ((self.provincia.nombre + ",") if self.provincia else "",
                                 (self.ciudad.nombre + ",") if self.ciudad else "",
                                 (self.direccion + ",") if self.direccion else "")


    def activo(self):
        return self.usuario.is_active

    def mi_cumpleannos(self):
        hoy = datetime.now().date()
        nacimiento = self.nacimiento
        if nacimiento.day == hoy.day and nacimiento.month == hoy.month:
            return True
        return False

    def edad(self):
        hoy = datetime.now().date()
        try:
            nac = self.nacimiento
            if hoy.year > nac.year:
                edad = hoy.year - nac.year
                if hoy.month <= nac.month:
                    if hoy.month == nac.month:
                        if hoy.day < nac.day:
                            edad -= 1
                    else:
                        edad -= 1
                return edad
            else:
                raise ()
        except:
            return 0

    def nombre_completo(self):
        return u'%s %s' % (self.apellido, self.nombre)

    def lista_telefonos(self):
        lista = []
        if self.celular:
            lista.append(self.celular)
        return lista

    def en_uso(self):
        if self.facturaventa_set.values('id').filter(status=True).exists():
            return True
        return False

    def save(self, *args, **kwargs):
        self.apellido = self.apellido.upper().strip()
        self.nombre = self.nombre.upper().strip()
        self.direccion = self.direccion.upper().strip()
        self.email = self.email.lower()
        super(Cliente, self).save(*args, **kwargs)

class Vendedor(ModeloBase):
    class TipoDocumento(models.IntegerChoices):
        NINGUNO = 0, "Ninguno"
        CEDULA = 1, "Cédula"
        PASAPORTE = 2, "Pasaporte"
        RUC = 3, "Ruc"

    tipodocumento = models.IntegerField(choices=TipoDocumento.choices, default=TipoDocumento.NINGUNO, blank=True, null=True,
                               verbose_name=u"Tipo Documento")
    identificacion = models.CharField(default='', max_length=13, verbose_name=u"Identificación")
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombres')
    apellido = models.CharField(default='', max_length=100, verbose_name=u"Apellidos")
    nacimiento = models.DateField(verbose_name=u"Fecha de nacimiento", null=True, blank=True)
    sexo = models.ForeignKey(Sexo, default=2, verbose_name=u'Sexo', on_delete=models.CASCADE)
    email = models.CharField(default='', max_length=200, verbose_name=u"Correo electronico personal")
    pais = models.ForeignKey(Pais, blank=True, null=True, verbose_name=u'País residencia', on_delete=models.SET_NULL)
    provincia = models.ForeignKey(Provincia, blank=True, null=True, verbose_name=u"Provincia de residencia", on_delete=models.SET_NULL)
    ciudad = models.ForeignKey(Ciudad, blank=True, null=True, verbose_name=u"Ciudad de residencia", on_delete=models.SET_NULL)
    direccion = models.CharField(default='', max_length=100, verbose_name=u"Calle principal", null=True, blank=True)
    celular = models.CharField(default='', max_length=50, verbose_name=u"Celular")
    usuario = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return u'%s %s' % (self.apellido, self.nombre)

    class Meta:
        verbose_name = u"Vendedor"
        verbose_name_plural = u"Vendedores"
        ordering = ['apellido', 'nombre']
        unique_together = ('identificacion',)

    @staticmethod
    def flexbox_query(q, extra=None):
        if extra:
            return eval('Vendedor.objects.filter(status=True,Q(apellido__icontains="%s") | Q(nombre__icontains="%s"),status=True).filter(%s).order_by("apellido")' % (q, q, extra))
        return Vendedor.objects.filter(Q(apellido__icontains=q) | Q(nombre__icontains=q),status=True).order_by('apellido')

    def flexbox_repr(self):
        return str(self.apellido) + " " + self.nombre

    def flexbox_alias(self):
        return [self.id, self.apellido, self.nombre]


    def direccion_completa(self):
        return u"%s %s %s" % ((self.provincia.nombre + ",") if self.provincia else "",
                              (self.ciudad.nombre + ",") if self.ciudad else "",
                              (self.direccion + ",") if self.direccion else "")

    def direccion_corta(self):
        return u"%s" % ((self.direccion + ",") if self.direccion else "")

    def activo(self):
        return self.usuario.is_active

    def mi_cumpleannos(self):
        hoy = datetime.now().date()
        nacimiento = self.nacimiento
        if nacimiento.day == hoy.day and nacimiento.month == hoy.month:
            return True
        return False

    def grupos(self):
        if self.usuario.groups.values("id").exists():
            return self.usuario.groups.all().distinct()
        return None

    def edad(self):
        hoy = datetime.now().date()
        try:
            nac = self.nacimiento
            if hoy.year > nac.year:
                edad = hoy.year - nac.year
                if hoy.month <= nac.month:
                    if hoy.month == nac.month:
                        if hoy.day < nac.day:
                            edad -= 1
                    else:
                        edad -= 1
                return edad
            else:
                raise ()
        except:
            return 0

    def nombre_completo(self):
        return u'%s %s' % (self.apellido, self.nombre)

    def lista_telefonos(self):
        lista = []
        if self.telefono:
            lista.append(self.telefono)
        if self.celular:
            lista.append(self.celular)
        return lista

    def en_uso(self):
        if self.sucursalvendedor_set.values('id').filter(status=True).exists():
            return True
        return False
        # return SucursalVendedor.objects.filter(vendedor=self) if SucursalVendedor.objects.values_list('id').filter(vendedor=self).exists() else None

    def obtener_todas_sucursales(self):
        if self.sucursalvendedor_set.values('id').exists():
            return self.sucursalvendedor_set.all()
        return None

    def tiene_cliente(self, cliente):
        return ClienteVendedor.objects.filter(status=True, cliente=cliente, vendedor=self).latest('id') if ClienteVendedor.objects.filter(status=True, cliente=cliente, vendedor=self).exists() else None

    def pertenece_sucursal(self, sucursal):
        return SucursalVendedor.objects.filter(status=True, sucursal=sucursal, vendedor=self)[0] if SucursalVendedor.objects.values_list('id').filter(status=True, sucursal=sucursal, vendedor=self).exists() else None

    def obtener_sucursal(self):
        vendedor = SucursalVendedor.objects.filter(status=True, vendedor=self)[0] if SucursalVendedor.objects.values_list('id').filter(status=True, vendedor=self).exists() else None
        return vendedor

    def necesita_cambiar_clave(self):
        return self.usuario.cambioclaveusuario_set.values("id").exists()

    def clave_cambiada(self):
        self.usuario.cambioclaveusuario_set.all().delete()

    def solicitud_cambio_clave(self, clave):
        if CambioClaveUsuario.objects.values("id").filter(usuario=self, clavecambio=clave).exists():
            return CambioClaveUsuario.objects.filter(usuario=self, clavecambio=clave)[0]
        return None

    def cambiar_clave(self):
        if self.usuario.cambioclaveusuario_set.values("id").exists():
            cc = self.usuario.cambioclaveusuario_set.all()[0]
            cc.solicitada = False
            cc.clavecambio = ""
        else:
            cc = CambioClaveUsuario(usuario=self.usuario)
        cc.save()
        return cc

    def save(self, *args, **kwargs):
        self.apellido = self.apellido.upper().strip()
        self.nombre = self.nombre.upper().strip()
        self.direccion = self.direccion.upper().strip()
        self.email = self.email.lower()
        super(Vendedor, self).save(*args, **kwargs)

class Sucursal(ModeloBase):
    class TipoSucursal(models.IntegerChoices):
        NINGUNO             = 0, "Ninguno"
        BODEGA            = 1, "BODEGA"
        SUCURSALVENTA             = 2, "SUCURSAL VENTA"
    tipo = models.IntegerField(choices=TipoSucursal.choices, default=TipoSucursal.NINGUNO, blank=True, null=True, verbose_name=u"Tipo Sucursal")
    nombre_comercial = models.TextField(default='', verbose_name=u'Nombre Comercial', null=True, blank=True)
    direccion = models.TextField(default='', verbose_name=u'Dirección', null=True, blank=True)
    telefono = models.CharField(default='', null=True, blank=True, max_length=15, verbose_name=u'Teléfono')
    email = models.CharField(default='', max_length=100, verbose_name=u'Email')
    actividad_economica = models.TextField(default='', verbose_name=u'Actividad Económica', null=True, blank=True)
    pais = models.ForeignKey(Pais, max_length=3, blank=True, null=True, verbose_name=u'País', on_delete=models.SET_NULL)
    provincia = models.ForeignKey(Provincia, max_length=3, blank=True, null=True, verbose_name=u'Provincia', on_delete=models.SET_NULL)
    ciudad = models.ForeignKey(Ciudad, max_length=8, blank=True, null=True, verbose_name=u'Ciudad', on_delete=models.SET_NULL)
    matriz = models.BooleanField(default=False, verbose_name=u'Es Matriz')

    def __str__(self):
        return u'%s (%s)' % (self.nombre_comercial, self.ciudad.nombre)

    class Meta:
        verbose_name = u"Sucursal"
        verbose_name_plural = u"Sucursales"
        ordering = ['matriz', 'nombre_comercial']

    @staticmethod
    def flexbox_query(q, extra=None):
        if extra:
            return eval('Sucursal.objects.filter(Q(nombre_comercial__icontains="%s") | Q(ciudad__nombre__icontains="%s"),status=True ).filter(%s).distinct()' % (q, q, extra))
        return Sucursal.objects.filter(Q(nombre_comercial__icontains=q) | Q(ciudad__nombre__icontains=q),status=True).distinct()

    def flexbox_repr(self):
        return str(self.nombre_comercial) + " - " + self.ciudad.nombre

    def flexbox_alias(self):
        return [self.id, self.nombre_comercial, self.ciudad.nombre]

    def direccion_completa(self):
        return u"%s %s %s" % ((self.provincia.nombre + ",") if self.provincia else "",
                                 (self.ciudad.nombre + ",") if self.ciudad else "",
                                 (self.direccion + ",") if self.direccion else "")

    def direccion_corta(self):
        return u"%s" % ((self.direccion + ",") if self.direccion else "")

    def en_uso(self):
        if self.sucursalvendedor_set.values('id').filter(status=True).exists():
            return True
        if self.movimientoinventario_set.values('id').filter(status=True).exists():
            return True
        if self.itemunidadmedidastock_set.values('id').filter(status=True).exists():
            return True
        if self.sucursalsecuencia_set.values('id').filter(status=True).exists():
            return True
        if self.transferencia_set.values('id').filter(status=True).exists():
            return True
        if self.transferenciadetalle_set.values('id').filter(status=True).exists():
            return True
        return False

    def nombre_completo(self):
        return u'%s (%s)' % (self.nombre_comercial, self.ciudad.nombre)

    def secuencia_factura(self):
        secuencia = None
        if not self.sucursalsecuencia_set.filter(status=True).exists():
            secuencia = SucursalSecuencia(sucursal=self)
            secuencia.save()
        else:
            secuencia = self.sucursalsecuencia_set.filter(status=True)[0]
        return secuencia

    def obtener_sucursal(self):
        vendedor = SucursalVendedor.objects.filter(status=True, sucursal=self)[0] if SucursalVendedor.objects.values_list('id').filter(status=True, sucursal=self).exists() else None
        return vendedor

    def obtener_secuencia(self):
        if self.sucursalsecuencia_set.values('id').exists():
            return self.sucursalsecuencia_set.filter(status=True)[0]
        return None

    def numero_facturas_hoy(self, usuario):
        cant=FacturaVenta.objects.values('id').filter(status=True,valida=True,fecha__icontains=datetime.now().date()).count()
        return cant

    def numero_ordenes_hoy(self, usuario):
        cant=0
        if usuario.is_superuser:
            if OrdenPedido.objects.values('id').filter(Q(fechapedido__icontains=datetime.now().date()),vendedor__sucursal=self,status=True).exists():
                cant= OrdenPedido.objects.values('id').filter(Q(fechapedido__icontains=datetime.now().date()),vendedor__sucursal=self,status=True).count()
        else:
            if OrdenPedido.objects.values('id').filter(Q(fechapedido__icontains=datetime.now().date()),vendedor__sucursal=self,status=True,vendedor__vendedor__usuario=usuario).exists():
                cant= OrdenPedido.objects.values('id').filter(Q(fechapedido__icontains=datetime.now().date()),vendedor__sucursal=self,status=True,vendedor__vendedor__usuario=usuario).count()
        return cant

    def monto_ordenes(self, usuario):
        suma=0
        if usuario.is_superuser:
            if OrdenPedidoDetalle.objects.values('id').filter(Q(ordenpedido__fechapedido__icontains=datetime.now().date()),ordenpedido__vendedor__sucursal=self,status=True).exists():
                suma=round_half_up( float(OrdenPedidoDetalle.objects.filter(Q(ordenpedido__fechapedido__icontains=datetime.now().date()),ordenpedido__vendedor__sucursal=self,status=True).aggregate(suma=Sum('total'))['suma']),2)
        else:
            if OrdenPedidoDetalle.objects.values('id').filter(Q(ordenpedido__fechapedido__icontains=datetime.now().date()),ordenpedido__vendedor__sucursal=self,status=True,ordenpedido__vendedor__vendedor__usuario=usuario).exists():
                suma = round_half_up(float(OrdenPedidoDetalle.objects.filter(Q(ordenpedido__fechapedido__icontains=datetime.now().date()),ordenpedido__vendedor__sucursal=self,status=True,ordenpedido__vendedor__vendedor__usuario=usuario).aggregate(suma=Sum('total'))['suma']),2)
        return suma



    def save(self, *args, **kwargs):
        self.nombre_comercial = self.nombre_comercial.upper()
        self.actividad_economica = self.actividad_economica.upper()
        self.direccion = self.direccion.upper()
        self.email = self.email.lower()
        super(Sucursal, self).save(*args, **kwargs)

class SucursalVendedor(ModeloBase):
    sucursal = models.ForeignKey(Sucursal, blank=True, null=True, verbose_name=u'Sucursal', on_delete=models.SET_NULL)
    vendedor = models.ForeignKey(Vendedor, blank=True, null=True, verbose_name=u'Vendedor', on_delete=models.SET_NULL)

    def __str__(self):
        return u'%s - %s' % (self.vendedor, self.sucursal)

    class Meta:
        verbose_name = u"Sucursal Vendedor"
        verbose_name_plural = u"Sucursales Vendedores"

    def en_uso(self):
        return self.facturaventa_set.values('id').filter(status=True).exists()

    def save(self, *args, **kwargs):
        super(SucursalVendedor, self).save(*args, **kwargs)
class AnioEjercicio(ModeloBase):
    anioejercicio = models.IntegerField(default=0, verbose_name=u"Ejercicio")

    def __str__(self):
        return u"%s" % self.anioejercicio

    @staticmethod
    def flexbox_query(q, extra=None):
        return AnioEjercicio.objects.filter(anioejercicio__icontains=q,status=True).distinct()

    def flexbox_repr(self):
        return u"%s" % self.anioejercicio

    def flexbox_alias(self):
        return [self.id, self.anioejercicio]

    def secuencia_factura_venta(self):
        if not SecuenciaFacturaVenta.objects.filter(status=True, anioejercicio=self).exists():
            secuencia = SecuenciaFacturaVenta(status=True, anioejercicio=self)
            secuencia.save()
            return secuencia
        else:
            return SecuenciaFacturaVenta.objects.filter(status=True, anioejercicio=self)[0]
class Impuesto(ModeloBase):
    codigo = models.CharField(default='', max_length=2, verbose_name=u'Código', null=True, blank=True)
    descripcion = models.CharField(default='', max_length=50, verbose_name=u'Descripción', null=True, blank=True)
    valor = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Valor")
    fechainicio = models.DateField(verbose_name=u'Fecha inicio', null=True, blank=True)
    fechafin = models.DateField(verbose_name=u'Fecha fin', null=True, blank=True)

    def __str__(self):
        return u'%s - %s' % (self.descripcion, self.valor)

    class Meta:
        verbose_name = u"Impuesto"
        verbose_name_plural = u"Impuestos"

    def en_uso(self):
        if self.item_set.values('id').filter(status=True).exists():
            return True
        if self.facturaventadetalle_set.values('id').filter(status=True).exists():
            return True
        return False

    def save(self, *args, **kwargs):
        super(Impuesto, self).save(*args, **kwargs)

class ItemCategoria(ModeloBase):
    descripcion = models.CharField(default='', max_length=100, verbose_name=u'Categoría', null=True, blank=True)

    def __str__(self):
        return u'%s' % (self.descripcion)

    class Meta:
        verbose_name = u"Categoría de Item"
        verbose_name_plural = u"Categorías de Items"

    @staticmethod
    def flexbox_query(q, extra=None):
        if extra:
            return eval('ItemCategoria.objects.filter( Q(descripcion__icontains="%s"),status=True ).filter(%s).order_by("descripcion")' % (q, extra))
        return ItemCategoria.objects.filter(Q(descripcion__icontains=q), status=True).order_by('descripcion')

    def flexbox_repr(self):
        return str(self.descripcion)

    def flexbox_alias(self):
        return [self.id, self.descripcion]

    def en_uso(self):
        if self.item_set.values('id').filter(status=True).exists():
            return True
        return False

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(ItemCategoria, self).save(*args, **kwargs)

class Marca(ModeloBase):
    descripcion = models.CharField(default='', max_length=150, verbose_name=u'Marca', null=True, blank=True)

    def __str__(self):
        return u'%s' % (self.descripcion)

    class Meta:
        verbose_name = u"Marca"
        verbose_name_plural = u"Marcas"

    def en_uso(self):
        if self.item_set.values('id').filter(status=True).exists():
            return True
        return False

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(Marca, self).save(*args, **kwargs)

class UnidadMedida(ModeloBase):
    unidad = models.CharField(default='', max_length=11, verbose_name=u'Unidad', null=True, blank=True)
    descripcion = models.CharField(default='', max_length=50, verbose_name=u'Descripción', null=True, blank=True)
    simbolo = models.CharField(default='', max_length=8, verbose_name=u'Símbolo', null=True, blank=True)

    def __str__(self):
        return u'%s (%s)' % (self.descripcion, self.simbolo)

    class Meta:
        verbose_name = u"Unidad medida"
        verbose_name_plural = u"Unidades Medidas"

    @staticmethod
    def flexbox_query(q, extra=None):
        if extra:
            return eval('UnidadMedida.objects.filter(Q(unidad__icontains="%s") | Q(descripcion__icontains="%s") | Q(simbolo__icontains="%s"),status=True ).filter(%s)' % (q, q,q, extra))
        return UnidadMedida.objects.filter(Q(unidad__icontains=q) | Q(descripcion__icontains=q)| Q(simbolo__icontains=q),status=True)

    def flexbox_repr(self):
        return u'%s (%s)' % (self.descripcion, self.simbolo)

    def flexbox_alias(self):
        return [self.id, self.descripcion, self.simbolo]

    def en_uso(self):
        if self.item_set.values('id').filter(status=True).exists():
            return True
        if self.itemunidadmedida_set.values('id').filter(status=True).exists():
            return True
        return False

    def nombre_completo(self):
        return u'%s (%s)' % (self.descripcion, self.simbolo)

    def save(self, *args, **kwargs):
        self.unidad = self.unidad.upper()
        self.descripcion = self.descripcion.upper()
        self.simbolo = self.simbolo.upper()
        super(UnidadMedida, self).save(*args, **kwargs)

class FormaPago(ModeloBase):
    descripcion = models.CharField(default='', max_length=100, verbose_name=u"Descripción")
    numdias = models.IntegerField(default=0, verbose_name=u"Número de dias plazo")

    def __str__(self):
        return u'%s' % self.descripcion

    class Meta:
        verbose_name = u"Forma pago"
        verbose_name_plural = u"Forma pago"
        ordering = ['descripcion']
        unique_together = ('descripcion', 'numdias')

    def en_uso(self):
        if self.facturacomprapago_set.values('id').filter(status=True).exists():
            return True
        if self.facturacompra_set.values('id').filter(status=True).exists():
            return True
        if self.facturaventa_set.values('id').filter(status=True).exists():
            return True
        if self.ordenpedido_set.values('id').filter(status=True).exists():
            return True
        return False

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        super(FormaPago, self).save(*args, **kwargs)
class Item(ModeloBase):
    codigo = models.CharField(default='', null=True, blank=True, max_length=30, verbose_name=u'Código')
    descripcion = models.CharField(default='', max_length=200, verbose_name=u'Descripción', null=True, blank=True)
    categoria = models.ForeignKey(ItemCategoria, blank=True, null=True, verbose_name=u'Categoria', on_delete=models.SET_NULL)
    marca = models.ForeignKey(Marca, blank=True, null=True, verbose_name=u'Marca', on_delete=models.SET_NULL)
    unidad_base = models.ForeignKey(UnidadMedida, blank=True, null=True, verbose_name=u'Unidad Medida Base', on_delete=models.SET_NULL)
    impuesto = models.ForeignKey(Impuesto, blank=True, null=True, verbose_name=u'Impuesto', on_delete=models.SET_NULL)

    def __str__(self):
        return u'%s (%s)  %s ' % (self.codigo, self.marca.descripcion,self.descripcion)

    class Meta:
        verbose_name = u"Item"
        verbose_name_plural = u"Items"

    @staticmethod
    def flexbox_query(q, extra=None):
        if extra:
            return eval('Item.objects.filter(Q(codigo__icontains="%s") | Q(descripcion__icontains="%s"),status=True ).filter(%s).order_by("descripcion")' % (q, q, extra))
        return Item.objects.filter(Q(codigo__icontains=q) | Q(descripcion__icontains=q),status=True).order_by('descripcion')

    def flexbox_repr(self):
        return str(self.codigo) + " - " + self.descripcion

    def flexbox_alias(self):
        return [self.id, self.codigo, self.descripcion]

    def nombre_completo(self):
        return u'%s / %s' % (self.codigo, self.descripcion)

    def en_uso(self):
        if self.itemunidadmedida_set.values('id').filter(status=True).exists():
            return True
        if self.facturacompracopiastock_set.values('id').filter(status=True).exists():
            return True
        if self.facturacompracopiadetalle_set.values('id').filter(status=True).exists():
            return True
        return False

    def puede_modificar(self):
        if ItemUnidadMedidaStock.objects.values('id').filter(itemunidadmedida__item=self, status=True).exists():
            return True
        if FacturaVentaDetalle.objects.values('id').filter(itemunidadmedidastock__itemunidadmedida__item=self, status=True).exists():
            return True
        return False

    def unidades_medida(self):
        if self.itemunidadmedida_set.filter(status=True).exists():
            return self.itemunidadmedida_set.filter(status=True).order_by('-orden')
        return None

    def ejecutar_conversion(self, sucursal):
        list = []
        unidadminima = ItemUnidadMedida.objects.filter(status=True, item=self, itemunidadmedidaequivalencia__status=True).order_by('orden')[0]
        stockminimo = ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida=unidadminima, sucursal=sucursal)[0]
        for itemunidadmedidabase in ItemUnidadMedida.objects.filter(status=True, item=self).order_by('-orden'):
            cantidadstock = 0
            equivalencia = None
            if ItemUnidadMedidaEquivalencia.objects.filter(status=True, itemunidadmedida__item=self,
                                                           unidad_medida_origen=itemunidadmedidabase.unidad_medida,
                                                           unidad_medida_fin=unidadminima).exists():
                equivalencia = ItemUnidadMedidaEquivalencia.objects.filter(status=True, itemunidadmedida__item=self,
                                                                           unidad_medida_origen=itemunidadmedidabase.unidad_medida,
                                                                           unidad_medida_fin=unidadminima)[0]
                if ItemUnidadMedidaStock.objects.filter(status=True, sucursal=sucursal, item=self, itemunidadmedida=itemunidadmedidabase).exists():
                    stock = ItemUnidadMedidaStock.objects.filter(status=True, sucursal=sucursal, item=self, itemunidadmedida=itemunidadmedidabase)[0]
                    cantidadconvertida = stockminimo.stock / float(equivalencia.equivalenciaumfin)
                    stock.stock = cantidadconvertida
                    stock.save()
        return True

    def view_stock_1(self, sucursal):
        if ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida__item=self,sucursal__id=sucursal).exists():
            return ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida__item=self,sucursal__id=sucursal).order_by('-itemunidadmedida__orden')
        return None

    def view_stock_conversion(self,sucursal):
        import math
        lista = []
        unidadmaxima= ItemUnidadMedida.objects.filter(status=True, item=self, itemunidadmedidaequivalencia__status=True).order_by('-orden')[0]
        stockummaxima = ItemUnidadMedidaStock.objects.filter(status=True, itemunidadmedida__unidad_medida=unidadmaxima.unidad_medida, itemunidadmedida__item=self, sucursal=sucursal)[0]
        cantidaddecimal=stockummaxima.stock
        for itemunidadmedidabase in ItemUnidadMedida.objects.filter(status=True, item=self).order_by('-orden'):
            equivalencia = None
            cantidadNueva=0
            if unidadmaxima.orden <= itemunidadmedidabase.orden:
                if unidadmaxima.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidabase.unidad_medida, unidad_medida_fin=unidadmaxima.unidad_medida).exists():
                    equivalencia = unidadmaxima.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=itemunidadmedidabase.unidad_medida, unidad_medida_fin=unidadmaxima.unidad_medida)[0]
                    cantidadNueva = float(cantidaddecimal) / float(equivalencia.equivalenciaumfin)
            else:
                if itemunidadmedidabase.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=unidadmaxima.unidad_medida, unidad_medida_fin=itemunidadmedidabase.unidad_medida).exists():
                    equivalencia = itemunidadmedidabase.itemunidadmedidaequivalencia_set.filter(status=True, unidad_medida_origen=unidadmaxima.unidad_medida, unidad_medida_fin=itemunidadmedidabase.unidad_medida)[0]
                    cantidadNueva = float(cantidaddecimal) * float(equivalencia.equivalenciaumfin)
            cantidaddecimal,cantidadentera=math.modf(cantidadNueva)
            cantidaddecimal=round_half_up(cantidaddecimal,4)
            lista.append([str(itemunidadmedidabase.unidad_medida), int(cantidadentera)])
            unidadmaxima = itemunidadmedidabase
        return lista

    def mis_sucursales(self):
        if ItemUnidadMedidaStock.objects.values('id').filter(status=True,itemunidadmedida__item=self).exists():
            ids=ItemUnidadMedidaStock.objects.values_list('sucursal_id',flat=True).filter(status=True,itemunidadmedida__item=self).distinct()
            return Sucursal.objects.filter(status=True, id__in=ids)
        return None

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        self.codigo = self.codigo.upper()
        super(Item, self).save(*args, **kwargs)

class ItemUnidadMedida(ModeloBase):
    item = models.ForeignKey(Item, blank=True, null=True, verbose_name=u'Item', on_delete=models.SET_NULL)
    unidad_medida = models.ForeignKey(UnidadMedida, blank=True, null=True, verbose_name=u'Unidad Medida', on_delete=models.SET_NULL)
    porcentaje_ganancia = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"% Ganancia")
    orden = models.IntegerField(default=0, verbose_name=u"Orden")

    def __str__(self):
        return u'%s / %s' % (self.item, self.unidad_medida)

    class Meta:
        verbose_name = u"Item Unidad de Medida"
        verbose_name_plural = u"Items Unidades de Medida"

    def en_uso(self):
        if self.detallemovimientoinventario_set.values('id').filter(status=True).exists():
            return True
        if self.itemunidadmedidastock_set.values('id').filter(status=True).exists():
            return True
        if self.transferenciadetalle_set.values('id').filter(status=True).exists():
            return True
        if self.ofertaitem_set.values('id').filter(status=True).exists():
            return True
        return False

    def nombre_completo(self):
        return "%s / %s" % (self.item.descripcion, self.unidad_medida.descripcion)

    def stock(self,sucursal):
        if self.itemunidadmedidastock_set.values('id').filter(status=True,sucursal=sucursal).exists():
            return self.itemunidadmedidastock_set.filter(status=True,sucursal=sucursal)[0]
        return None

    def save(self, *args, **kwargs):
        super(ItemUnidadMedida, self).save(*args, **kwargs)

class ItemUnidadMedidaEquivalencia(ModeloBase):
    itemunidadmedida = models.ForeignKey(ItemUnidadMedida, blank=True, null=True, verbose_name=u'Item Unidad medida', on_delete=models.SET_NULL)
    valorumorigen = models.IntegerField(default=1, blank=True, null=True, verbose_name=u'Valor Unidad de medida origen')
    unidad_medida_origen = models.ForeignKey(UnidadMedida, blank=True, null=True, related_name='+', verbose_name=u'Unidad Medida origen', on_delete=models.SET_NULL)
    equivalenciaumfin = models.DecimalField(default=0, max_digits=30, decimal_places=4,blank=True, null=True, verbose_name=u'Valor Unidad de medida origen')
    unidad_medida_fin = models.ForeignKey(UnidadMedida, blank=True, null=True, related_name='+', verbose_name=u'Unidad Medida finaliza', on_delete=models.SET_NULL)
    orden = models.IntegerField(default=0, verbose_name=u"Orden")

    def __str__(self):
        return u'Item: %s | U.M.O: %s | U.MF: %s ' % (self.itemunidadmedida, self.unidad_medida_origen, self.unidad_medida_fin)

    def save(self, *args, **kwargs):
        super(ItemUnidadMedidaEquivalencia, self).save(*args, **kwargs)


class ItemUnidadMedidaStock(ModeloBase):
    itemunidadmedida = models.ForeignKey(ItemUnidadMedida, blank=True, null=True, verbose_name=u'Item', on_delete=models.SET_NULL)
    sucursal = models.ForeignKey(Sucursal, blank=True, null=True, verbose_name=u'Sucursal', on_delete=models.SET_NULL)
    costo_unitario = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Costo Unitario")
    precio = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Precio Unitario Máximo")
    preciominimo = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Precio Unitario Mínimo")
    stock = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Stock")
    impuesto = models.ForeignKey(Impuesto, null=True, blank=True, verbose_name=u'Impuesto', on_delete=models.SET_NULL)
    valorimpuesto = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Valor impuesto")
    costototal = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"costo total")
    porcentaje_ganancia = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"% Ganancia")
    ganancia = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"% Ganancia")

    def __str__(self):
        return u'Sucursal: %s | Item: %s - Stock Disponible: %s' % (self.sucursal, self.itemunidadmedida, self.stock )

    class Meta:
        verbose_name = u"Item por Unidad de Medida"
        verbose_name_plural = u"Items por Unidades de Medida"
    def nombre_completo(self):
        return u'Sucursal: %s | Item: %s - Stock Disponible: %s' % (self.sucursal, self.itemunidadmedida, self.stock )

    def stock_actual(self):
        return int(self.stock) if self.stock >= 1 else 0

    def stock_disponible(self):
        return int(self.stock ) if self.stock >= 1 else 0

    def en_uso(self):
        if self.facturaventadetalle_set.values('id').filter(status=True).exists():
            return True
        if self.ordenpedidodetalle_set.values('id').filter(status=True).exists():
            return True
        if self.notacreditodetalle_set.values('id').filter(status=True).exists():
            return True
        return False

    def nombre_item(self):
        return u'%s (%s)  %s ' % (self.itemunidadmedida.item.codigo, self.itemunidadmedida.item.marca.descripcion,self.itemunidadmedida.item.descripcion)

    def nombre_unidad_medida(self):
        return self.itemunidadmedida.unidad_medida.descripcion


    def save(self, *args, **kwargs):
        super(ItemUnidadMedidaStock, self).save(*args, **kwargs)


class FacturaVenta(ModeloBase):
    class TipoFacturaVenta(models.IntegerChoices):
        NINGUNO = 0, "Ninguno"
        NOTAVENTA = 1, "Nota de venta"
        FACTURAVENTA = 2, "Factura de venta"

    numero = models.IntegerField(default=0, verbose_name=u'Numero de factura')
    codigo = models.CharField(default='', blank=True, null=True, max_length=50, verbose_name=u"Código")
    documento = models.FileField(upload_to='archivoFacturaVenta/%Y/%m/%d/', blank=True, null=True, verbose_name=u'Documento Archivado')
    cliente = models.ForeignKey(Cliente, null=True, blank=True, verbose_name=u'Cliente', on_delete=models.SET_NULL)
    vendedor = models.ForeignKey(SucursalVendedor, null=True, blank=True, verbose_name=u'Vendedor', on_delete=models.SET_NULL)
    formapago = models.ForeignKey(FormaPago, null=True, blank=True, verbose_name=u'Formapago', on_delete=models.SET_NULL)
    fechafactura = models.DateTimeField(verbose_name=u'Fecha de factura', null=True, blank=True)
    direccionentrega = models.CharField(default='', max_length=200, verbose_name=u'Direccion entrega', null=True, blank=True)
    subtotal = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Sub total")
    valorimpuesto = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Valor impuesto")
    total = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"Total")
    efectivorecibido = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"efectivo recibido")
    cambio = models.DecimalField(default=0, max_digits=30, decimal_places=2, verbose_name=u"cambio")
    valida = models.BooleanField(default=True, verbose_name=u"Valida")
    pagada = models.BooleanField(default=False, verbose_name=u"Pagada")
    tipo = models.IntegerField(choices=TipoFacturaVenta.choices, default=TipoFacturaVenta.NOTAVENTA, verbose_name=u'Tipo de factura de venta')

    def __str__(self):
        return u'%s - %s' % (self.codigo, self.cliente.nombre_completo())

    class Meta:
        verbose_name = u"Factura venta"
        verbose_name_plural = u"Facturas venta"

    def download_link(self):
        if self.documento:
            return self.documento.url

    def cantidad_productos(self):
        if self.facturaventadetalle_set.filter(status=True).exists():
            return self.facturaventadetalle_set.values('id').filter(status=True).count()
        return 0

    def puede_devolver_tiempo(self):
        hoy = datetime.now()
        fechaafactura = self.fechafactura
        total = fechaafactura + timedelta(days=1)
        if hoy <= total:
            return True
        else:
            return False
    def total_forma_pago(self):
        if self.facturaventaformapago_set.values('id').filter(status=True).exists():
            return self.facturaventaformapago_set.filter(status=True).exclude(formapago__numdias__gte=1).aggregate(suma=Sum('valor'))['suma']
        return 0

    def obtener_forma_pago(self):
        if self.facturaventaformapago_set.values('id').filter(status=True).exists():
            return self.facturaventaformapago_set.filter(status=True)
        return None

    def valor_por_pagar(self):
        if self.pagada:
            return 0
        if self.total_forma_pago():
            saldo = self.total - self.total_forma_pago()
        else:
            saldo=self.total
        return saldo

    def actualizar_valores_cabecera(self):
        if self.facturaventadetalle_set.values('id').filter(status=True).exists():
            self.subtotal = self.facturaventadetalle_set.filter(status=True).aggregate(valor=Sum('subtotal'))['valor']
            self.valorimpuesto = self.facturaventadetalle_set.filter(status=True).aggregate(valor=Sum('valorimpuesto'))['valor']
            self.total = self.facturaventadetalle_set.filter(status=True).aggregate(valor=Sum('total'))['valor']
        self.save()
        return self.total

    def subtotal_cero(self):
        if self.facturaventadetalle_set.filter(status=True, impuesto__valor=0).exists():
            return self.facturaventadetalle_set.filter(status=True, impuesto__valor=0).aggregate(valor=Sum('subtotal'))['valor']
        return 0

    def subtotal_doce(self):
        if self.facturaventadetalle_set.filter(status=True, impuesto__valor__gt=0).exists():
            return self.facturaventadetalle_set.filter(status=True, impuesto__valor__gt=0).aggregate(valor=Sum('subtotal'))['valor']
        return 0

    def detalles(self):
        return self.facturaventadetalle_set.filter(status=True)
    def save(self, *args, **kwargs):
        super(FacturaVenta, self).save(*args, **kwargs)

class FacturaVentaFormaPago(ModeloBase):
    formapago = models.ForeignKey(FormaPago, null=True, blank=True, verbose_name=u'Formapago', on_delete=models.SET_NULL)
    facturaventa = models.ForeignKey(FacturaVenta, null=True, blank=True, verbose_name=u'Factura venta', on_delete=models.SET_NULL)
    valor = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Valor")
    observacion = models.TextField(default='', max_length=500, verbose_name=u'Observación', null=True, blank=True)


class FacturaVentaDetalle(ModeloBase):
    facturaventa = models.ForeignKey(FacturaVenta, null=True, blank=True, verbose_name=u'Factura venta', on_delete=models.SET_NULL)
    itemunidadmedidastock = models.ForeignKey(ItemUnidadMedidaStock, null=True, blank=True, verbose_name=u'Item unidad medida', on_delete=models.SET_NULL)
    cantidad = models.IntegerField(default=0, verbose_name=u'Cantidad ')
    costo = models.DecimalField(default=0,null=True, blank=True, max_digits=30, decimal_places=4, verbose_name=u"Costo")
    precio = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Precio")
    subtotal = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Sub total")
    impuesto = models.ForeignKey(Impuesto, null=True, blank=True, verbose_name=u'Impuesto', on_delete=models.SET_NULL)
    valorimpuesto = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Valor impuesto")
    total = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Total")
    porcentaje_ganancia = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Porcentaje ganancia")
    ganancia = models.DecimalField(default=0, max_digits=30, decimal_places=4, verbose_name=u"Ganancia")

    def __str__(self):
        return u'%s - %s' % (self.facturaventa, self.itemunidadmedidastock)

    class Meta:
        verbose_name = u"Factura venta detalle"
        verbose_name_plural = u"Facturas ventas detalles"

    def save(self, *args, **kwargs):
        super(FacturaVentaDetalle, self).save(*args, **kwargs)


class ModeloEjemplo(ModeloBase):
    class Estado(models.IntegerChoices):
        NINGUNO = 0, "Ninguno"
        APROBADO = 1, "APROBADO"
        RECHAZADO = 2, "RECHAZADO"
        PENDIENTE = 3, "PENDIENTE"

    estado = models.IntegerField(choices=Estado.choices, default=Estado.NINGUNO, blank=True, null=True, verbose_name=u"Estado")
    valor = models.DecimalField(default=0, max_digits=10,decimal_places=2, verbose_name=u"valor nota")
    cantidad= models.IntegerField(default=0, verbose_name=u"catidad")
    codigo = models.CharField(max_length=10, blank=True, null=True, verbose_name=u"codigo")
    descripcion = models.TextField(blank=True, null=True, verbose_name=u"descripción")
    pais= models.ForeignKey(Pais,blank=True, null=True, verbose_name=u"Pais", on_delete=models.SET_NULL)
    opcion = models.ManyToManyField(OpcionModulo, verbose_name=u'Opcion de modulo')
    fechaInicio = models.DateField(verbose_name=u"Fecha de inicio",default=datetime.now().date(), null=True, blank=True)
    fechaFin = models.DateTimeField(verbose_name=u'Fecha de fin',auto_now=True, null=True, blank=True)
    archivo = models.FileField(upload_to='archivoEjemplo/%Y/%m/%d/', blank=True, null=True, verbose_name=u'Archivo')


