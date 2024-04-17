import os
from datetime import datetime

from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import Q
from django.forms.models import ModelForm
from django.forms.widgets import DateTimeInput, FileInput
from django.utils.safestring import mark_safe
from app.models import *


class CheckboxSelectMultipleCustom(forms.CheckboxSelectMultiple):
    def render(self, *args, **kwargs):
        output = super(CheckboxSelectMultipleCustom, self).render(*args, **kwargs)
        return mark_safe(output.replace(u'<ul>',
                                        u'<div class="custom-multiselect" style="width: 600px;overflow: scroll"><ul>').replace(
            u'</ul>', u'</ul></div>').replace(u'<li>', u'').replace(u'</li>', u'').replace(u'<label',
                                                                                           u'<div style="width: 900px"><li').replace(
            u'</label>', u'</li></div>'))


class ExtFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]
        self.max_upload_size = kwargs.pop("max_upload_size")
        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        upload = super(ExtFileField, self).clean(*args, **kwargs)
        if upload:
            size = upload.size
            filename = upload.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()
            if size == 0 or ext not in self.ext_whitelist or size > self.max_upload_size:
                raise forms.ValidationError("Tipo de fichero o tamanno no permitido!")


class FixedForm(ModelForm):
    date_fields = []

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for f in self.date_fields:
            self.fields[f].widget.format = '%d-%m-%Y'
            self.fields[f].input_formats = ['%d-%m-%Y']


def deshabilitar_campo(form, campo):
    form.fields[campo].widget.attrs['readonly'] = True
    form.fields[campo].widget.attrs['disabled'] = True


def habilitar_campo(form, campo):
    form.fields[campo].widget.attrs['readonly'] = False
    form.fields[campo].widget.attrs['disabled'] = False


def campo_solo_lectura(form, campo):
    form.fields[campo].widget.attrs['readonly'] = True

class VendedorForm(forms.Form):
    tipodocumento = forms.ChoiceField(label=u'Tipo identificación', choices=Vendedor.TipoDocumento.choices,
                             initial=Vendedor.TipoDocumento.NINGUNO,
                             widget=forms.Select(attrs={'class': 'form-select', 'col': '4'}),
                             error_messages={'required': 'Seleccione el tipo de facilitador (requerido)'})
    identificacion = forms.CharField(max_length=200, label=u'Identificación', required=False,
                                     widget=forms.TextInput(attrs={'class': 'form-control', 'col': '4'}))
    nacimiento = forms.DateField(label=u"Fecha nacimiento", initial=datetime.now().date(),
                                 required=False, input_formats=['%Y-%m-%d'],
                                 widget=DateTimeInput(format='%Y-%m-%d',
                                                      attrs={'class': 'form-control', 'col': '4', 'type': 'date'}))
    nombre = forms.CharField(label=u"Nombres", max_length=400, required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'col': '12'}))
    apellido = forms.CharField(label=u"Apellidos", max_length=400, required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'col': '12'}))

    sexo = forms.ModelChoiceField(Sexo.objects.filter(status=True), required=False, label=u'Sexo',
                                  widget=forms.Select(attrs={'class': 'form-control','col': '6'}))
    email = forms.CharField(max_length=200, label=u'Email', required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control','col': '6'}))
    pais = forms.ModelChoiceField(Pais.objects.filter(status=True), required=False, label=u'Pais residencia',
                                  widget=forms.Select(attrs={'col': '4'}))
    provincia = forms.ModelChoiceField(Provincia.objects.filter(status=True), required=False,
                                       label=u'Provincia residencia',
                                       widget=forms.Select(attrs={'col': '4'}))
    ciudad = forms.ModelChoiceField(Ciudad.objects.filter(status=True), required=False, label=u'Ciudad residencia',
                                    widget=forms.Select(attrs={'col': '4'}))
    direccion = forms.CharField(label=u"Dirección", max_length=400, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control','col': '12'}))
    celular = forms.CharField(initial=0, required=False, label=u'Celular.',
                              widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'col': '6', }))
    sucursal = forms.ModelChoiceField(Sucursal.objects.filter(status=True,tipo=2), required=False, label=u'Sucursal',
                                      widget=forms.Select(attrs={'class': 'multi-option','col': '6'}))
    username = forms.CharField(label=u"Nombre de usuario", max_length=400, required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    password = forms.CharField(label=u'Clave', required=False,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'col': '6'}))

    def editar(self):
        deshabilitar_campo(self, 'identificacion')
        del self.fields['username']
        del self.fields['password']
        del self.fields['sucursal']

class GrupoForm(forms.Form):
    name = forms.CharField(label=u'Nombre', required=False, max_length=250,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'col': '12'}))

class GrupoUsuarioForm(forms.Form):
    grupo = forms.ModelMultipleChoiceField(label=u'Grupos', queryset=Group.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class': 'fomr-control multi-option', 'multiple': 'multiple', 'col': '12'}))

    def grupos(self, lista):
        self.fields['grupo'].queryset = lista


class ItemForm(forms.Form):
    codigo = forms.CharField(label=u"Código", max_length=30, required=False,widget=forms.TextInput(attrs={'class': 'form-control','col': '12'}))
    categoria = forms.ModelChoiceField(ItemCategoria.objects.filter(status=True), required=False,  label=u'Categoria de item', widget=forms.Select(attrs={'col': '12'}))
    descripcion = forms.CharField(label=u"Descripción", max_length=400, required=False, widget=forms.TextInput(attrs={'class': 'form-control','col': '12'}))
    marca = forms.ModelChoiceField(Marca.objects.filter(status=True), required=False, label=u'Marca', widget=forms.Select(attrs={'col': '12'}))
    unidad_base = forms.ModelChoiceField(UnidadMedida.objects.filter(status=True), required=False,  label=u'Unidad de medida base', widget=forms.Select(attrs={ 'col': '12'}))
    impuesto = forms.ModelChoiceField(Impuesto.objects.filter(status=True), required=False, label=u'Impuesto', widget=forms.Select(attrs={'col': '12'}))

    def editar(self):
        deshabilitar_campo(self, 'codigo')

class ItemUnidadMedidaForm(forms.Form):
    unidad_medida = forms.ModelChoiceField(UnidadMedida.objects.filter(status=True), required=False,
                                           label=u'Unidad de medida',
                                           widget=forms.Select(attrs={'class': 'multi-option', 'col': '12'}))
    porcentaje_ganancia = forms.DecimalField(initial=0, label=u'Porcentaje de ganancia', required=False,
                                             widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                             'col': '6'}))

    orden = forms.IntegerField(initial=0, required=False, label=u'Orden',
                               widget=forms.NumberInput(attrs={'class': 'form-control', 'col': '2'}))

    def excluirUnidadesUsadas(self, ids):
        self.fields['unidad_medida'].queryset = UnidadMedida.objects.filter(status=True).exclude(id__in=ids)


class FacturaVentaCabeceraForm(forms.Form):
    hoy = datetime.now().date()
    cliente = forms.IntegerField(initial=1, required=False, label=u'Cliente', widget=forms.TextInput(attrs={'select2search': 'true', 'width_control': 'col-lg-6 col-md-6 col-sm-12 col-12'}))
    tipo = forms.ChoiceField(label=u'Tipo de emisión', choices=FacturaVenta.TipoFacturaVenta.choices,
                                      initial=FacturaVenta.TipoFacturaVenta.NOTAVENTA,
                                      widget=forms.Select(attrs={'class': 'form-select', 'col': '4'}),
                                      error_messages={'required': 'Seleccione el tipo de facilitador (requerido)'})
    fechafactura = forms.DateField(label=u"Fecha documento", initial=datetime.now().date(),
                                   required=False, input_formats=['%d-%m-%Y'],
                                   widget=DateTimeInput(format='%d-%m-%Y',
                                                        attrs={'class': 'form-control', 'width_control': 'col-lg-3 col-md-6 col-sm-6 col-6'}))
    direccionentrega = forms.CharField(label=u"Observación", max_length=400, required=False,
                                       widget=forms.Textarea(attrs={'class': 'form-control', 'col': '12','rows':"1"}))

    def adicionar_cabecera(self):
        deshabilitar_campo(self, 'fechafactura')
        self.fields['cliente'].widget.attrs['descripcion'] = Cliente.objects.get(id=1).flexbox_repr()
        self.fields['cliente'].widget.attrs['value'] = 1

class FacturaVentaDetalleForm(forms.Form):
    item = forms.ModelChoiceField(Item.objects.filter(status=True), required=False, label=u'Item',
                                  widget=forms.Select(attrs={'class': 'multi-option form-control form-control-sm', 'style': 'width:auto'}))
    unidadmedida = forms.ModelChoiceField(UnidadMedida.objects.filter(status=True), required=False,
                                          label=u'Unidad Medida',
                                          widget=forms.Select(
                                              attrs={'class': 'multi-option form-control form-control-sm', 'style': 'width:150px;'}))
    cantidad = forms.DecimalField(initial=1, required=False, label=u'Cantidad',
                                  widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-right', 'style': 'width:85px;'}))
    stock = forms.DecimalField(initial=0, required=False, label=u'Cantidad Dispo',
                               widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-right', 'style': 'width:85px;'}))
    precio = forms.DecimalField(initial=0, required=False, label=u'Precio',
                                widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-right', 'style': 'width:85px;'}))
    subtotal = forms.DecimalField(initial=0, required=False, label=u'Sub total',
                                  widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-right', 'style': 'width:85px;'}))
    valorimpuesto = forms.DecimalField(initial=0, required=False, label=u'IVA',
                                       widget=forms.NumberInput(
                                           attrs={'class': 'form-control form-control-sm text-right', 'style': 'width:85px;'}))
    total = forms.DecimalField(initial=0, required=False, label=u'Total',
                               widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-right', 'style': 'width:85px;'}))

    def adicionar(self, sucursal):
        if ItemUnidadMedidaStock.objects.values_list('itemunidadmedida__item_id').filter(status=True, sucursal=sucursal).exists():
            self.fields['item'].queryset = Item.objects.filter(status=True, id__in=ItemUnidadMedidaStock.objects.values_list('itemunidadmedida__item_id'
                                                                                                                             ).filter(Q(stock__gte=1),
                                                                                                                                      status=True, sucursal=sucursal))
        else:
            self.fields['item'].queryset = Item.objects.filter(id=0)
        deshabilitar_campo(self, 'stock')
        deshabilitar_campo(self, 'subtotal')
        deshabilitar_campo(self, 'valorimpuesto')
        deshabilitar_campo(self, 'total')
class FacturaVentaFormaPagoForm(forms.Form):
    formapago = forms.ModelChoiceField(FormaPago.objects.filter(status=True).exclude(id=2).order_by('descripcion'), required=False,
                                       label=u'Forma pago',
                                       widget=forms.Select(attrs={'class': 'multi-option form-control form-control-sm', 'width_control': '150px'}))
    valor = forms.DecimalField(initial=0, required=False, label=u'Valor',
                               widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-right', 'width_control': '85px'}))
    observacion = forms.CharField(label=u'Observación',
                                  widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'width_control': '150px'}))
    def adicionar(self):
        self.fields['formapago'].initial = 6