function edit_future_date_handler(e){
  e.preventDefault();
  $this = $(this);
  var divParent = $this.parents('.future-wrapper');
  divParent.find('p').toggle();
  divParent.find('.hidden').toggle();
  text = $this.text() == 'Edit' ? 'Cancel' : 'Edit';
  $this.text(text);
}

function update_future_date(e){
  e.preventDefault();
  var $this = $(this);
  var future_date = $this.siblings('.future_date');
  var formData = {}
  
  formData[ future_date.attr('name') ] = new Date(future_date.val()).toUTCString();

  $.post(FUTURE_URL, formData, function(data){
    $this.parents('.future-wrapper').html(data);
  });
}

function verify_survey_close(e)
{
  var x = confirm('This will permanently close this survey, are you sure?')
  if( !x ){
  e.preventDefault(); 
  }
}

function clone_survey_dialog(e){
  e.preventDefault();
  $('#clone-form').dialog({ 
      title:'Clone Survey',
      resizable:false,
      disabled:true,
      modal:true,
      hide:'fold',
      close:function(e,ui){
        $(this).dialog('destroy');
      }
    });
}

$.ready = function()
{
  $('#close_survey').click(verify_survey_close);
  $('#clone').click(clone_survey_dialog);
  $('input[name="submit-clone"]').click(function(e){
    e.preventDefault();
    var div = $(this).closest('div');
    var cloneElement = div.find('input[name="clone"]');
    var title = cloneElement.val();
    var url = cloneElement.attr('data-url');
    $.post(url, {'title':title})
      .success(function(data){
        if( 'error' in data ){
          div.find('.error').html(data.error);
        }
        else{
          window.location = data.url
        }
      })
      .error(function(){
        div.find('.error').html('An error has occurred and the survey has not been cloned.\nPlease try again.');
      });
  });
}