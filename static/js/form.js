var _url = window.location.toString().split(window.location.host.toString())[1];
var cargando = '<i class="fa fa-cog fa-spin" role="status" aria-hidden="true"></i>';
var error_btn2 = '<i class="fa fa-check-circle" role="status" aria-hidden="true"></i> Guardar';
var method_req = "POST";
var _enc = $('*[data-datoseguro=true]').toArray();
var headerId = '#header';
var __enc = [];
for (var i = 0; i < _enc.length; i++) {
    __enc.push($(_enc[i]).attr('name'));
}
var inputsEncrypted = __enc.join('|');
$(function () {
    $('form:not([method=GET], [method=get])').submit(function (e) {
        e.preventDefault();
        if (typeof funcionAntesDeGuardar === 'function') {
            funcionAntesDeGuardar();
        }
        const formulario = $(this);
        const btnSubmit = $('#submit');
        const error_btn = btnSubmit.html();
        $('input, textarea, select').removeClass('is-invalid');
        const pk = formulario.find('input[name=pk]').length ? parseInt(formulario.find('input[name=pk]').val()) : 0;
        const action = formulario.find('input[name=action]').length ? formulario.find('input[name=action]').val() : false;
        const _url = formulario.find('input[name=urlsubmit]').length ? formulario.find('input[name=urlsubmit]').val() : window.location.toString().split(window.location.host.toString())[1];
        var _form = new FormData(formulario[0]);
        if (pk !== 0) {
            if (_form.has('pk')) {
                _form.set('pk', pk.toString());
            } else {
                _form.append('pk', pk.toString());
            }

        }
        if (action !== false) {
            if (_form.has('action')) {
                _form.set('action', action);
            } else {
                _form.append('action', action);
            }
        }
        const listInputsEnc = inputsEncrypted.split('|');
        for (var i = 0; i < listInputsEnc.length; i++) {
            if (_form.has(listInputsEnc[i])) {
                _form.set(listInputsEnc[i], doRSA(_form.get(listInputsEnc[i])));
            }
        }
        try {
            _form.append("lista_items1", JSON.stringify(lista_items1));
        } catch (err) {
            console.log(err.message);
        }

        $.ajax({
            type: method_req,
            url: _url,
            data: _form,
            dataType: "json",
            enctype: formulario.attr('enctype'),
            cache: false,
            contentType: false,
            processData: false,
            beforeSend: function () {
                btnSubmit.html(cargando);
                btnSubmit.attr("disabled", true);
                bloquearpantalla();
            }
        }).done(function (data) {
            if (!data.result) {
                if(data.modalname){
                    $('#'+data.modalname).modal('hide');
                } else {
                    $(".modal").modal('hide');
                }
                if (data.to) {
                    if (data.modalsuccess) {
                        $.unblockUI();
                        $('#textpanelmensaje').html(data.mensaje);
                        $('#returnpanelmensaje').attr("href", data.to);
                        $('#waitpanelmensaje').modal({backdrop: 'static'}).modal('show');
                    } else {
                        location = data.to;
                    }
                } else if(data.cerrar){
                    $.unblockUI();
                    Swal.fire(data.mensaje, '', 'success')
                } else {
                    if (data.modalsuccess) {
                        $.unblockUI();
                        $('#textpanelmensaje').html(data.mensaje);
                        $('#returnpanelmensaje').attr('onClick','location.reload()');
                        $('#waitpanelmensaje').modal({backdrop: 'static'}).modal('show');
                    } else {
                        location.reload();
                    }

                }
            }
            else if (data.data_return){
                $.unblockUI();
                alertaSuccess(data.mensaje)
                btnSubmit.html(error_btn2);
                btnSubmit.attr("disabled", false);
                ActualizarTabla(data.data)
            } else {
                if (data.form) {
                    $(".mensaje_error").empty()
                    data.form.forEach(function (val, indx) {
                        var keys = Object.keys(val);
                        keys.forEach(function (val1, indx1) {
                            $("#id_" + val1).addClass("is-invalid");
                            $("#errorMessage" + val1).html(val[val1]);
                        });
                    });
                }
                alertaDanger(data.mensaje);
                btnSubmit.html(error_btn2);
                btnSubmit.attr("disabled", false);
                $.unblockUI();
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            btnSubmit.html(error_btn2);
            btnSubmit.attr("disabled", false);
            $.unblockUI();
        }).always(function () {

        });
    });
});

