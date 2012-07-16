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
    var $choice =
    $('<div>').addClass('choice').css('margin-left', '1em').append(
        $('<label>').html('Choice: ').attr('for', 'asdf').after(
        $('<input>').attr('type', 'text').attr('name', 'choice-message').after(
        $('<button>').attr('type', 'button').html('Remove').click(removeChoice))).after(
        $('<br>')
    ));
    $button.parent().find('.new-choice').before($choice);
}

function newMultiQuestionHandler(questionType){
    return function(){
        var $question =
        $('<div>').addClass('question').append(
            $('<label>').html('Message: ').attr('for', 'asdf').after(
            $('<input>').attr('type', 'hidden').attr('name', 'question-type').val(questionType).after(
            $('<input>').attr('type', 'text').attr('name', 'question-message').after(
            $('<button>').attr('type', 'button').html('Remove').click(removeQuestion))).after(
            $('<button>').attr('type', 'button').addClass('new-choice').html('New choice').click(newChoice)
        )));
        $('#new-buttons').before($question);
        // Start with two blank choices
        $question.find('.new-choice').click();
        $question.find('.new-choice').click();
    }
}

function newQuestionHandler(questionType){
    return function(){
        var $question =
        $('<div>').addClass('question').append(
            $('<label>').html('Message: ').attr('for', 'asdf').after(
            $('<input>').attr('type', 'hidden').attr('name', 'question-type').val(questionType).after(
            $('<input>').attr('type', 'text').attr('name', 'question-message').after(
            $('<button>').attr('type', 'button').html('Remove').click(removeQuestion)
        ))));
        $('#new-buttons').before($question);
    };
}

var newTextArea = newQuestionHandler('TA');
var newTextBox = newQuestionHandler('TB');
var newCheckBoxes = newMultiQuestionHandler('CH');
var newRadioButtons = newMultiQuestionHandler('RA');
var newDropDownList = newMultiQuestionHandler('DD');

$.ready = function(){
    $('#submit').click(function(e){
        var url = SURVEY_INDEX + URLify($('#title').val())+'/';
        var data = {title: $('#title').val(), questions: []};
        $('.question').each(function(index, el){
            var $el = $(el);
            var questionData = {};
            questionData.type = $el.find('input[name="question-type"]').val();
            questionData.message = $el.find('input[name="question-message"]').val();
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
            'success':function(){
                window.location=url;
            }
        });
    });
    $('#new-text-area').click(newTextArea);
    $('#new-text-box').click(newTextBox);
    $('#new-check-boxes').click(newCheckBoxes);
    $('#new-radio-buttons').click(newRadioButtons);
    $('#new-drop-down-list').click(newDropDownList);
}
