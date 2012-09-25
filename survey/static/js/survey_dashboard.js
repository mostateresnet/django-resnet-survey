$(document).ready(function(){
  // http://trentrichardson.com/examples/timepicker/
  $("input[name='future_date']").datetimepicker({
    addSliderAccess: true,
    sliderAccessArgs: { touchonly: false },
    ampm: true,
    minDate: new Date()
  });
});