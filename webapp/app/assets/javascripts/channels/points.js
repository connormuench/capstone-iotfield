var rawChartData;
var chart;

$(document).ready(function() {
    if ($("#pointChart").length > 0) {
        chart = Chartkick.charts["chart"];
        rawChartData = cloneChartData(chart.getData());

        App.points = []
        App.points.push(App.cable.subscriptions.create({channel: "PointsChannel", point_id: $("#pointChart").data("point-id")}, {
            connected: function() {
                console.log("connected");
            },
            disconnected: function() {
                console.log("disconnected");
            }, 
            received: function(data) {
                rawChartData.forEach(function(series) {
                    if (series.id === data.point_id) {
                        series.data.push([moment(data.created_at).toDate(), data.value]);
                    }
                });
                if ($("#autoUpdateChart").is(":checked")) {
                    if ($("#pointChart").is(":hidden")) {
                        $("#pointChart").show();
                    }
                    updateChart();
                }
            }
        }));

        $('#startDatetimepicker').datetimepicker({defaultDate: moment().subtract(14, "days")});
        $('#endDatetimepicker').datetimepicker({defaultDate: moment().add(14, "days")});

        updateChart();
    }
});

function cloneChartData(data) {
    let clone = [];
    data.forEach(function(series) {
        let newSeries = {};
        newSeries.id = series.id;
        newSeries.name = series.name;
        newSeries.data = [];
        series.data.forEach(function(point) {
            newSeries.data.push([point[0], point[1]]);
        });
        clone.push(newSeries);
    });
    return clone;
}

function filterChartByDate(startDate, endDate, chartData) {
    let filteredData = cloneChartData(chartData);
    
    if (startDate >= endDate) {
        filteredData.forEach(function(series) {
            series.data = [];
        });
        return filteredData;
    }

    filteredData.forEach(function(series) {
        let newData = [];
        series.data.forEach(function(point) {
            let date = point[0];
            if (date >= startDate && date <= endDate) {
                newData.push([point[0], point[1]]);
            }
        });
        series.data = newData;
    });

    return filteredData;
}

function updateChart() {
    let startDate = $("#startDatetimepicker").datetimepicker("viewDate");
    let endDate = $("#endDatetimepicker").datetimepicker("viewDate");
    
    chart.updateData(filterChartByDate(startDate, endDate, rawChartData));
}
