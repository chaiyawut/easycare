<script>
$(function () {
    var chart;
    $(document).ready(function() {
        $.getJSON('/records/drug_graph/{{ record.patient.id }}/', function(data) {
            var drugs = [];

            data.drugs.forEach(function(entry, idx) {
                drugs.push([Date.UTC(entry.year,  entry.month-1, entry.day), entry.total]);
            });

            console.log(drugs[0]);

            chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'drug_graph_container',
                    zoomType: 'x',
                    spacingRight: 20
                },
                title: {
                    text: 'ข้อมูลการรับประทานยาของผู้ป่วย'
                },
                subtitle: {
                    text: document.ontouchstart === undefined ?
                        'Click and drag in the plot area to zoom in' :
                        'Drag your finger over the plot to zoom in'
                },
                xAxis: {
                    type: 'datetime',
                    maxZoom: 9 * 24 * 3600000, // fourteen days
                    title: {
                        text: null
                    },
                },
                yAxis: {
                    title: {
                        text: 'ยาลิซิก (มิลิกรัม)'
                    },
                    min:0
                },
                tooltip: {
                    shared: true
                },
                legend: {
                    enabled: false
                },
                plotOptions: {
                    area: {
                        fillColor: {
                            linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                            stops: [
                                [0, Highcharts.getOptions().colors[0]],
                                [1, 'rgba(2,0,0,0)']
                            ]
                        },
                        lineWidth: 1,
                        marker: {
                            enabled: false,
                            states: {
                                hover: {
                                    enabled: true,
                                    radius: 5
                                }
                            }
                        },
                        dataLabels: {
                            enabled: true
                        },
                        shadow: false,
                        states: {
                            hover: {
                                lineWidth: 1
                            }
                        },
                        threshold: null
                    }
                },
        
                series: [{
                    type: 'area',
                    name: 'ปริมาณยาลิซิก',
                    //pointInterval: 24 * 3600 * 1000,
                    //pointStart: Date.UTC(2013, 0, 01),
                    //data: data.morning_weights
                    data: drugs
                }]
            });
        });
    });
});
</script>