<script>
$(function () {
    var chart;
    $(document).ready(function() {
        $.getJSON('/records/{{ record.id }}/graph/pressure/', function(data) {

            chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'pressure_graph_container',
                    type: 'column'
                },
                title: {
                    text: 'สรุปความดันย้อนหลัง 7 วัน'
                },
                xAxis: [{
                    categories: data.last_7_days,
                    labels: {
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                }],
                yAxis: {
                    title: {
                        text: 'ความดัน (มม.ปรอท.)'
                    },
                    labels: {
                        formatter: function(){
                            return Math.abs(this.value);
                        }
                    },
                },
        
                plotOptions: {
                    series: {
                        stacking: 'normal'
                    }
                },
        
                tooltip: {
                    formatter: function(){
                        return this.point.category +'<br/>'+
                            '<b>' + this.series.name + '</b>: ' + Highcharts.numberFormat(Math.abs(this.point.y), 0);
                    }
                },
        
                series: [{
                    name: 'ตัวบนเช้า',
                    data: data.last_7_days_morning_pressure_up,
                    stack: 'morning',
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        x: 3,
                        formatter: function() {
                            return Highcharts.numberFormat(Math.abs(this.y), 0);
                        },
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                }, {
                    name: 'ตัวล่างเช้า',
                    data: data.last_7_days_morning_pressure_down,
                    stack: 'morning',
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        x: 3,
                        formatter: function() {
                            return Highcharts.numberFormat(Math.abs(this.y), 0);
                        },
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                },{
                    name: 'ตัวบนกลางวัน',
                    data: data.last_7_days_afternoon_pressure_up,
                    stack: 'afternoon',
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        x: 3,
                        formatter: function() {
                            return Highcharts.numberFormat(Math.abs(this.y), 0);
                        },
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                }, {
                    name: 'ตัวล่างกลางวัน',
                    data: data.last_7_days_afternoon_pressure_down,
                    stack: 'afternoon',
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        x: 3,
                        formatter: function() {
                            return Highcharts.numberFormat(Math.abs(this.y), 0);
                        },
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                },{
                    name: 'ตัวบนเย็น',
                    data: data.last_7_days_evening_pressure_up,
                    stack: 'evening',
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',
                        x: 3,
                        formatter: function() {
                            return Highcharts.numberFormat(Math.abs(this.y), 0);
                        },
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                }, {
                    name: 'ตัวล่างเย็น',
                    data: data.last_7_days_evening_pressure_down,
                    stack: 'evening',
                    dataLabels: {
                        enabled: true,
                        rotation: -90,
                        color: '#FFFFFF',       
                        x: 3,
                        formatter: function() {
                            return Highcharts.numberFormat(Math.abs(this.y), 0);
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