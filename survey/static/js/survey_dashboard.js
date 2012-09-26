$(document).ready(function(){
  // http://trentrichardson.com/examples/timepicker/
  $("input[name='future_close_date'], input[name='future_publish_date']").datetimepicker({
    addSliderAccess: true,
    sliderAccessArgs: { touchonly: false },
    ampm: true,
    minDate: new Date()
  });
  
  $('.edit-handler').click(function(e){
    e.preventDefault();
    $this = $(this);
    var divParent = $this.parents('.future-wrapper');
    divParent.find('p').toggle();
    divParent.find('.hidden-form').toggle();
    text = $this.text() == 'Edit' ? 'Cancel' : 'Edit';
    $this.text(text);
  });
});