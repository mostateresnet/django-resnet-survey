// Load the Visualization API
  google.load('visualization', '1');
  // Set a callback to run when the Google Visualization API is loaded.
  google.setOnLoadCallback(setUpGraphs);

function drawChart( graphdiv ) {
  var table = graphdiv.siblings('.result').find('table');
  var data = [['','']];
  table.find('tr').each(function(){
    var tds = $(this).children('td');
      // push the name of the field removing and whitespace
      // as well as the number of items in that field
      data.push([$(tds[0]).text().replace(/[\n\t:]/g, ''), parseInt($(tds[1]).text())]);
  });
  var wrapper = new google.visualization.ChartWrapper({
    chartType: 'PieChart',
    dataTable: data,
    options: {'title': graphdiv.siblings('.result').find('label').text()},
    containerId: graphdiv.attr('id')
  });
  wrapper.draw();
}

function setUpGraphs(){
  $('.piegraph').each(function(){
    drawChart( $(this) );
  });
}