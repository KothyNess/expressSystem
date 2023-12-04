document.addEventListener("DOMContentLoaded", function () {
    function createChart(chartId, chartData) {
        var chartDom = document.getElementById(chartId);
        var myChart = echarts.init(chartDom);
        var option = {
            xAxis: {
                type: 'category',
                data: chartData.categories
            },
            yAxis: {
                type: 'value'
            },
            series: [
                {
                    data: chartData.values,
                    type: 'bar',
                    showBackground: true,
                    backgroundStyle: {
                        color: 'rgba(180, 180, 180, 0.2)'
                    }
                }
            ]
        };
        myChart.setOption(option);
    }

    // 使用这个函数为每一个图表创建实例
    createChart('staffChart', chartsData['staff_chart']);
});
