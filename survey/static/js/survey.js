$(document).ready(function()
{
    $('form').submit(function(e)
    {
      $('.required').each(function(index, el)
      {
          el = $(el)
          field_name = el.find("div[role=heading] span").text();
          if (field_name == "") { field_name = el.find("label span").text();  }
          abort = ((el.is(".question_type_TB") && el.children("input")[0].value == "") ||
          (el.is(".question_type_TA") && el.children("textarea")[0].value == "") ||
          (el.is(".question_type_RA") && !el.find("input[type=radio]").is(":checked")) ||
          (el.is(".question_type_CH") && !el.find("input[type=checkbox]").is(":checked")) ||
          (el.is(".question_type_DD") && el.find("select").val() == "_BAD_"))

          if (abort)
          { 
            alert("Missing Required field: [" + field_name+ "]"); 
            e.preventDefault();
            e.stopPropagation();
            return false;                    
          } 
        
      });
    });
});

