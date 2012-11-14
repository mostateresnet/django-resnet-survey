$(document).ready(function()
{
  $('.accordion').click(function(e) 
  {
      //ToDo: Try fadeToggle
      if ($(this).hasClass("expanded") || $(this).hasClass("collapsed"))
      {
        $(this).toggleClass("expanded");
        $(this).toggleClass("collapsed"); 
      }

      if ($(this).hasClass("slow"))
      { $(this).siblings("ul").toggle('slow'); }
      else
      { $(this).siblings("ul").toggle(); }

      return false;

  }).siblings("ul").hide();
});


