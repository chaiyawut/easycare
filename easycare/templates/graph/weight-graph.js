<script>
$(function () {
    var chart;
    $(document).ready(function() {
        $.getJSON('/records/{{ record.id }}/graph/weight/', function(data) {
            chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'weight_graph_container',
                    type: 'column',
                },
                title: {
                    text: 'สรุปน้ำหนักย้อนหลัง 7 วัน'
                },
                xAxis: {
                    categories: data.last_7_days,
                    labels: {
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                },
                yAxis: {
                    title: {
                        text: 'น้ำหนัก (กิโลกรัม)'
                    }
                },
                series: [{
                    name: 'เช้า',
                    data: data.last_7_days_morning_weights,
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        align: 'right',
                        x: 3,
                        y: 20,
                        formatter: function() {
                            return this.y;
                        },
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                },{
                    name: 'กลางวัน',
                    data: data.last_7_days_afternoon_weights,
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        align: 'right',
                        x: 3,
                        y: 20,
                        formatter: function() {
                            return this.y;
                        },
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                },{
                    name: 'เย็น',
                    data: data.last_7_days_evening_weights,
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        align: 'right',
                        x: 3,
                        y: 20,
                        formatter: function() {
                            return this.y;
                        },
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                }]
            });
        });
    });
});
</script>