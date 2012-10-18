$(document).ready(function() {
    $(".ul-tree span.expandable").click(function(e){
        $(e.currentTarget).toggleClass("expanded", $(e.currentTarget).hasClass("collapsed"));
        $(e.currentTarget).toggleClass("collapsed");
        if($.browser.msie){
            if($(e.currentTarget).hasClass("collapsed")){
                $(e.currentTarget).find("+ ul").css('display', 'none');
            }else{
                $(e.currentTarget).find("+ ul").css('display', 'block');
            }
        }
    });
});
