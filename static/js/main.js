/**
 * Created by p0wontnx on 5/2/17.
 */

google.charts.load('current', {packages: ['corechart', 'line']});


function drawLogScales(water_data) {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'X');
    data.addColumn('number', 'Quantity of water');
    data.addColumn({type: 'string', role: 'annotation'});
    data.addColumn({type: 'string', role: 'annotationText'});

    for (var date in water_data) {
        if (water_data.hasOwnProperty(date)) {
            data.addRow([date.substring(9, 14), Math.round(water_data[date]), 'P', 'P']);
        }
    }

    var options = {
        series: {
            0: {
                // set any applicable options on the first series
                colors: ['#a52714']
            },
            1: {
                // set the options on the second series
                lineWidth: 0,
                pointSize: 5,
                visibleInLegend: false
            }
        },
        hAxis: {
            title: 'Time',
            logScale: true
        },
        vAxis: {
            title: 'Quantity of water in mm',
            logScale: false
        }
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    chart.draw(data, options);
}

function loadData() {
    $.get('/api/water', function (data) {
        drawLogScales(JSON.parse(data))
    })
}

var startDrawingChart = function () {
    console.log('cb');
    loadData()
    setInterval(function () {
        loadData()
    }, 10000);
};

google.charts.setOnLoadCallback(startDrawingChart);
