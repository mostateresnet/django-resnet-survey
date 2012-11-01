jQuery(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});


$.fn.ajaxSubmit = function( options ) {
    this.each(function() {
        var settings = {
            'type': $(this).attr('method'),
            'url': $(this).attr('action'),
            'data': $(this).serialize(),
        };
        // If options exist, merge them
        // with default settings
        if ( options !== undefined ) { 
            $.extend( settings, options );
        }
        return $.ajax(settings);
    });
    return this;
};

function removeQuestion(e){
    $removableDiv = $(e.currentTarget).closest('.question');
    $removableDiv.remove();
}

function removeChoice(e){
    $removableDiv = $(e.currentTarget).closest('.choice');
    if ($removableDiv.siblings('.choice').length >= 2){
        $removableDiv.remove();
    }
}

function newChoice(e){
    $button = $(e.currentTarget);
    var $choice = $button.siblings('.choice').first().clone();
    $choice.find('input').val('');
    $button.parent().find('.new-choice').before($choice);
}

function newQuestionHandler(questionType){
    return function(){
        var $question = $(QUESTION_SOURCES[questionType]);
        $('#new-buttons').before($question);
    };
}

var newTextArea = newQuestionHandler('TA');
var newTextBox = newQuestionHandler('TB');
var newCheckBoxes = newQuestionHandler('CH');
var newRadioButtons = newQuestionHandler('RA');
var newDropDownList = newQuestionHandler('DD');

$.ready = function(){
    $('#submit').click(function(e){
        var data = {title: $('#title').val(), questions: []};
        $('.question').each(function(index, el){
            var $el = $(el);
            var questionData = {};
            questionData.type = $el.find('input[name="question-type"]').val();
            questionData.message = $el.find('input[name="question-message"]').val();
            questionData.required = $el.find('input[name="question-required"]').is(":checked");
            var choices = [];
            $el.find('input[name="choice-message"]').each(function(choiceIndex, choiceEl){
                choices.push($(choiceEl).val());
            });
            if (choices.length > 0){
                questionData.choices = choices;
            }
            data.questions.push(questionData);
        });
        $.ajax({
            'url': window.location,
            'type': 'POST',
            'data': {'r': JSON.stringify(data)},
            'success':function(data, textStatus, jqXHR){
                window.location = data['url'];
            }
        });
    });
    $('#new-text-area').click(newTextArea);
    $('#new-text-box').click(newTextBox);
    $('#new-check-boxes').click(newCheckBoxes);
    $('#new-radio-buttons').click(newRadioButtons);
    $('#new-drop-down-list').click(newDropDownList);
    $('.new-choice').live('click', newChoice);
    $('.remove-choice').live('click', removeChoice);
    $('.remove-question').live('click', removeQuestion);
}
