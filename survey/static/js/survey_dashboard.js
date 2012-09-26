$(document).ready(function(){
  // http://trentrichardson.com/examples/timepicker/
  $("input[name='future_close_date'], input[name='future_publish_date']").datetimepicker({
    addSliderAccess: true,
    sliderAccessArgs: { touchonly: false },
    ampm: true,
    minDate: new Date()
  });
});