<script>
$(function () {
    var chart;
    $(document).ready(function() {
        $.getJSON('/records/pressure_graph/{{ record.patient.id }}/', function(data) {
            var pressures_up = [];
            var pressures_down = [];

            data.pressures.up.forEach(function(entry, idx) {
                pressures_up.push([Date.UTC(entry.year,  entry.month-1, entry.day), entry.value]);
            });
            data.pressures.down.forEach(function(entry, idx) {
                pressures_down.push([Date.UTC(entry.year,  entry.month-1, entry.day), entry.value]);
            });

            chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'pressure_graph_container',
                    zoomType: 'x',
                    spacingRight: 20
                },
                title: {
                    text: 'ข้อมูลความดันของผู้ป่วย'
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
                        text: 'ความดัน (มม.ปรอท)'
                    },
                },
                tooltip: {
                    shared: true
                },
                legend: {
                    enabled: false
                },
                plotOptions: {
                    area: {
                        lineWidth: 1,
                        fillColor: {
                            linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                            stops: [
                                [0, Highcharts.getOptions().colors[0]],
                                [1, 'rgba(2,0,0,0)']
                            ]
                        },
                        marker: {
                            enabled: false,
                            states: {
                                hover: {
                                    enabled: true,
                                    radius: 5
                                }
                            }
                        },
                        shadow: false,
                        dataLabels: {
                            enabled: true
                        },
                        states: {
                            hover: {
                                lineWidth: 1
                            }
                        },
                        threshold: null
                    },
                },
                series: [{
                    type: 'area',
                    name: 'ความดันตัวบน',
                    //pointInterval: 24 * 3600 * 1000,
                    //pointStart: Date.UTC(2013, 0, 01),
                    //data: data.morning_weights
                    data: pressures_up
                },{
                    type: 'area',
                    name: 'ความดันตัวล่าง',
                    //pointInterval: 24 * 3600 * 1000,
                    //pointStart: Date.UTC(2013, 0, 01),
                    //data: data.morning_weights
                    data: pressures_down
                }]
            });
        });
    });
});
</script>