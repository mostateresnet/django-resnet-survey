jQuery.fn.collapser = function(persistant)
{      
  return this.each(function(){
    $(this).click(function(){

     $(this).toggleClass("expanded");

      if ( $(this).hasClass("expanded") )
      { $(this).siblings("ul").show('slow'); }
      else
      { $(this).siblings("ul").hide('slow'); }


    if (persistant)
      {
        var persistant_list = listFromCookie($(this).attr('id'));
        var cookie_data = parseNodeId($(this).attr('id'));

        if (cookie_data.cookie_id in persistant_list)
          { delete persistant_list[cookie_data.cookie_id]; }
        else
          { persistant_list[cookie_data.cookie_id] = true; }

        createCookie(cookie_data.cookie_cat + "_persistance", JSON.stringify(persistant_list));
      }

    });
    
    var $this = $(this);
    $this.ready(function()
    {
        var persistant_list = listFromCookie($this.attr('id'));
        var cookie_data = parseNodeId($this.attr('id'));
        if (cookie_data.cookie_id in persistant_list)
        {
          if (!$this.hasClass("expanded"))
          { $this.toggleClass("expanded"); }
          $this.siblings("ul").show();
        }
        else
        {
          $this.siblings("ul").hide();
        }
    });

   }); 
};


function parseNodeId(id_str)
{
  var id_sep = id_str.indexOf("_");
  var cookie_cat = id_str.substr(0,id_sep);
  var cookie_id = id_str.substr(id_sep+1);
  return { "cookie_cat": cookie_cat, "cookie_id": cookie_id };
}

function listFromCookie(id_str)
{
    var cookie_data = parseNodeId(id_str);        

    var current_cookie = readCookie(cookie_data.cookie_cat + "_persistance");
    var persistant_list = JSON.parse(current_cookie);

    // JSON.parse returns NULL if current_cookie is missing
    // So in that case we create the list manually
    if (!persistant_list)
      { persistant_list = {}; }

    return persistant_list;
}


