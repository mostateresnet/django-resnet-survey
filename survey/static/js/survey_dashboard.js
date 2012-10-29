function edit_future_date_handler(e){
  e.preventDefault();
  $this = $(this);
  var divParent = $this.parents('.future-wrapper');
  divParent.find('p').toggle();
  divParent.find('.hidden-form').toggle();
  text = $this.text() == 'Edit' ? 'Cancel' : 'Edit';
  $this.text(text);
}

function update_future_date(e){
  e.preventDefault();
  var $this = $(this);
  var future_date = $this.siblings('.future_date');
  var formData = {}
  formData[ future_date.attr('name') ] = future_date.val();
  $.post(FUTURE_URL, formData, function(data){
    $this.parents('.future-wrapper').html(data);
  });
}