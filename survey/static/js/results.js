// Load the Visualization API
google.load('visualization', '1');
// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(setUpGraphs);

function drawChart(graphdiv) {
    var table = graphdiv.siblings('table');
    var data = [['','']];
    var color = '';
    var font = '';
    table.find('tr').each(function(){
        var tds = $(this).children('td');
        // push the name of the field removing and whitespace
        // as well as the number of items in that field
        var label = $(tds[0]);
        data.push([label.text().replace(/[\n\t]/g, ''), parseInt($(tds[1]).text())]);
        color = label.css('color');
        font = label.css('font-family');
        console.log(font);
    });
    var wrapper = new google.visualization.ChartWrapper({
        chartType: 'PieChart',
        dataTable: data,
        options: {'backgroundColor': 'transparent', 'legend': {'textStyle': {'color': color, 'fontName': font}}},
        containerId: graphdiv.attr('id')
    });
    wrapper.draw();
}

function setUpGraphs() {
    $('.piegraph').each(function(){
        drawChart($(this));
    });
}

$(document).ready(function(){
    $('#excel-report-button').click(function(e){
        var EXPORT_EXCEL_URL = $(this).attr('data-export-url');
        var export_type = $('#excel-report-select').val();
        window.location.href = EXPORT_EXCEL_URL + "?rtype="+export_type;
    });
});


