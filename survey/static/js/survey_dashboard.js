function save_survey_duration(e)
{
    e.preventDefault();
    var data = {};
    data.start_date = $('input[name="start-date"]').val();
    data.start_time = $('input[name="start-time"]').val();
    data.end_date = $('input[name="end-date"]').val();
    data.end_time = $('input[name="end-time"]').val();
    data.set_duration = "";
    if(data.end_time === "")
    { delete data.end_time; }

    var old_sd = $('#survey-duration').attr('data-start-date-time');

    if (!old_sd && (data.start_date || data.start_time))
    { 
      if (!confirm('Once a survey gets ballots it cannot be modified or unpublished, are you sure you wish to publish this survey?'))
      { return; } 
    }

    $.post($(this).attr('data-url'), data, function(response)
    {
    if('errors' in response)
    { alert(response.errors); }
    else
    { location.reload(); }

    });
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

$(document).ready(function(){

  $('#delete_survey').click(function(e)
  {
    if (!confirm('Delete this survey?'))
    { return; } 

    var data = {};
    var refresh_url = $(this).attr('data-refresh');
    $.post($(this).attr('data-href'), data, function(r)
    { window.location = refresh_url; });      
  });
   
  $('#clone').click(clone_survey_dialog);
  $('input[name="set-duration"]').click(save_survey_duration);
  // Datepicker
  $('input[name="start-date"], input[name="end-date"]').not(':disabled').datepicker({
    showOn: "button",
    buttonImageOnly: true,
    buttonText: "Click to pick a date.",
    minDate:new Date(),
  });
  // to remove the space preserved by the relative positiong
  // there needs to be an absolutely positioned wrapper
  $('.ui-datepicker-trigger').wrap('<span class="absolute" />');
  // Timepicker
  $('input[name="start-time"], input[name="end-time"]').timepicker({ 
    'scrollDefaultNow': true,
    'step': 15
  });
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
});
