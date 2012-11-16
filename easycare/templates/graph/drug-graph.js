<script>
$(function () {
    var chart;
    $(document).ready(function() {
    	$.getJSON('/records/{{ record.id }}/graph/drug/', function(data) {
    		chart = new Highcharts.Chart({
	            chart: {
	                renderTo: 'drug_graph_container',
	                type: 'areaspline',
	            },
	            title: {
	                text: 'สรุปการรับประทานยาย้อนหลัง 7 วัน'
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
	                    text: 'ขนาด (มก.)'
	                },
	            },
	            plotOptions: {
	                areaspline: {
	                    fillOpacity: 0.5,
	                    dataLabels: {
	                        enabled: true
	                    },
	                },
	            },
	            series: [{
	                name: 'ลาซิก',
	                data: data.last_7_days_drug_consume_amounts
	            }]
	        });
    	});
    });
});
</script>