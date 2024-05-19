function tabla_paginacion(idtabla) {
    $(idtabla + "tbody").remove();

    var programs_table = $(idtabla).DataTable({
        sPaginationType: "simple_numbers",
        responsive: true,
        ordering: false,
        paging: true,
        searching: true,
        language: {
            "url": "/static/bootstrap5/libs/datatables.net-bs5/js/es-ES.json"
        },
        dom: 'Bfrtip',
        buttons: [],
        columnDefs: [
            {
                targets: 0,
                width: '80%',
            },
            {
                targets: 1,
                width: '10%',
                className: 'text-center',
            }

        ],
    });
    // return programs_table;
}

function GraficoRadial(idgrafico, title, subtitle, type, nametype = 'Clics', data) {
    Highcharts.chart(idgrafico, {
        chart: {
            polar: true
        },

        title: {
            text: title
        },

        subtitle: {
            text: subtitle
        },

        pane: {
            startAngle: 0,
            endAngle: 360
        },

        xAxis: {
            tickInterval: 45,
            min: 0,
            max: 360,
            labels: {
                format: '{value}°'
            }
        },

        yAxis: {
            min: 0
        },

        plotOptions: {
            series: {
                pointStart: 0,
                pointInterval: 45
            },
            column: {
                pointPadding: 0,
                groupPadding: 0
            }
        },

        series: [{
            type: type,
            name: nametype,
            data: [8, 7, 6, 5, 4, 3, 2, 1],
            pointPlacement: 'between'
        },
        ]
    });
}

function GraficoBurbuja(idgrafico, title, data, name = 'Clics') {
    Highcharts.setOptions({
        lang: {
            printChart: "Imprimir gráfico",
            viewFullscreen: "Ver pantalla completa",
            decimalPoint: ',',
            thousandsSep: '.',
            months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            weekdays: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            exportButtonTitle: "Exportar",
            printButtonTitle: "Imprimir",
            rangeSelectorFrom: "Desde",
            rangeSelectorTo: "Hasta",
            rangeSelectorZoom: "Período",
            downloadPNG: 'Descargar imagen PNG',
            downloadJPEG: 'Descargar imagen JPEG',
            downloadPDF: 'Descargar documento PDF',
            downloadSVG: 'Descargar imagen SVG',
            downloadCSV: "Descargar CSV",
            downloadXLS: "Descargar XLS",
            resetZoom: 'Reiniciar zoom',
            resetZoomTitle: 'Reiniciar zoom al nivel 1:1',
            noData: 'No hay datos para mostrar',
            drillUpText: 'Volver a {series.name}',
            exitFullscreen: 'Salir de pantalla completa',
            viewData: "Ver tabla de datos",
            hideData: "Ocultar tabla de datos"
            // Categories: "Nombres",
            // tableHideView: 'Ocultar tabla de datos',
        }
    });

    var chart = Highcharts.chart(idgrafico, {
        chart: {
            type: 'packedbubble',
            animation: false,
            height: '100%'
        },
        title: {
            text: title,
            align: 'center'
        },
        tooltip: {
            useHTML: true,
            pointFormat: '<b>{point.name}:</b> {point.value} ' + name
        },
        xAxis: {
            type: 'name'
        },
        yAxis: {
            title: {
                text: 'value'
            }
        },
        plotOptions: {
            packedbubble: {
                minSize: '5%',
                maxSize: '500%',
                zMin: 0,
                zMax: 1000,
                layoutAlgorithm: {
                    splitSeries: false,
                    gravitationalConstant: 0.02
                },
                dataLabels: {
                    enabled: true,
                    format: '{point.value}',
                    filter: {
                        property: 'value',
                        operator: '>',
                        value: 0
                    },
                    style: {
                        color: 'black',
                        textOutline: 'none',
                        fontWeight: 'normal'
                    }
                }
            }
        },
        series: data
    });

    return chart;
}

function ActualizarGrafico(chart, newseries) {
    chart.update({
        series: newseries
    });
}

function ActualizarMapa(mapacalor, links) {
    mapacalor.redefine("links", links);
}

function ActualizarTabla(tabla, datos) {
    let Existe = false;
    datos.forEach(function (elemento) {
        Existe = false;
        // Verificar si el elemento ya existe en la tabla
        tabla.row(function (idx, data, node) {
            if (data[0] === elemento[0]) {
                Existe = true;
            }
        }).data();
        if (Existe) {
            // Si el elemento existe, actualizar los valores de la fila
            tabla.row(function (idx, data, node) {
                return data[0] === elemento[0];
            }).data([
                elemento[0],
                elemento[1]
            ]).draw();
        } else {
            // Si el elemento no existe, agregar una nueva fila a la tabla
            tabla.row.add([
                elemento[0],
                elemento[1]
            ]).draw();
        }
    });
}

