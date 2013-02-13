function createCookie(name,value,days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
    // returns either the value of the cookie 'name'
    // or if it doesn't exist, returns null.
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name,"",-1);
}

$(function(){
    $(document).on('focus', '[placeholder]', function() {
        var input = $(this);
        if (input.val() == input.attr('placeholder')) {
            input.val('');
            input.toggleClass('placeholder', false);
        }
    }).on('blur', '[placeholder]', function() {
        var input = $(this);
        if (input.val() == '' || input.val() == input.attr('placeholder')) {
            input.toggleClass('placeholder', true);
            input.val(input.attr('placeholder'));
        }
    });
    $('[placeholder]').blur();
});
