<script>
$(function () {
    var chart;
    $(document).ready(function() {
        $.getJSON('/records/weight_graph/{{ record.patient.id }}/', function(data) {
            var morning_weights = [];
            var afternoon_weights = [];
            var evening_weights = [];

            data.weights.morning.forEach(function(entry, idx) {
                morning_weights.push([Date.UTC(entry.year,  entry.month-1, entry.day), entry.weight]);
            });
            data.weights.afternoon.forEach(function(entry, idx) {
                afternoon_weights.push([Date.UTC(entry.year,  entry.month-1, entry.day), entry.weight]);
            });
            data.weights.evening.forEach(function(entry, idx) {
                evening_weights.push([Date.UTC(entry.year,  entry.month-1, entry.day), entry.weight]);
            });

            chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'weight_graph_container',
                    zoomType: 'x',
                    spacingRight: 20
                },
                title: {
                    text: 'ข้อมูลน้ำหนักของผู้ป่วย'
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
                        text: 'น้ำหนัก (กิโลกรัม)'
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
                        fillColor: {
                            linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                            stops: [
                                [0, Highcharts.getOptions().colors[0]],
                                [1, 'rgba(2,0,0,0)']
                            ]
                        },
                        lineWidth: 1,
                        dataLabels: {
                            enabled: true
                        },
                        marker: {
                            enabled: true,
                            states: {
                                hover: {
                                    enabled: true,
                                    radius: 5
                                }
                            }
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
                    name: 'น้ำหนัก (เช้า)',
                    //pointInterval: 24 * 3600 * 1000,
                    //pointStart: Date.UTC(2013, 0, 01),
                    //data: data.morning_weights
                    data: morning_weights
                },{
                    type: 'area',
                    name: 'น้ำหนัก (กลางวัน)',
                    //pointInterval: 24 * 3600 * 1000,
                    //pointStart: Date.UTC(2013, 0, 01),
                    //data: data.morning_weights
                    data: afternoon_weights
                },{
                    type: 'area',
                    name: 'น้ำหนัก (เย็น)',
                    //pointInterval: 24 * 3600 * 1000,
                    //pointStart: Date.UTC(2013, 0, 01),
                    //data: data.morning_weights
                    data: evening_weights
                }]
            });
        });
    });
});
</script>