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

function newChoice(e)
{
    newChoiceDynamic($(e.currentTarget).parent().siblings('.choices'), "");
}

function newChoiceDynamic(parent, value)
{
    var $last_choice = parent.find('.choice').last()
    var $choice = $last_choice.clone();
    $last_choice.after($choice);
    $choice.find('input').val(value).blur();
}

function newQuestionHandler(questionType){
    return function(){
        var $question = $(QUESTION_SOURCES[questionType]);
        $('#questions').append($question);
        $question.find('[placeholder]').blur();
        initializeSortables();
    };
}

function initializeSortables(){
    $("#questions").sortable({
        handle: ".question-number",
        distance: 5,
        axis: 'y',
        forcePlaceholderSize: true,        
        placeholder: 'ui-state-highlight',
        cursor: 'move',
    });  
    $(".choices").sortable({
        distance: 5,
        axis: 'y',
        cursor: 'move',
        placeholder: 'ui-state-highlight',
        forcePlaceholderSize: true, 
    }); 
}

var newTextArea = newQuestionHandler('TA');
var newTextBox = newQuestionHandler('TB');
var newCheckBoxes = newQuestionHandler('CH');
var newRadioButtons = newQuestionHandler('RA');
var newDropDownList = newQuestionHandler('DD');


$(document).ready(function(){
    $('#submit').click(function(e){
        // Restrict the tile to reasonable bounds.
        if (($('#title').val().length < 1) || ($('#title').val().length > 1024))
        {
          alert('Survey Titles must be between 1 and 1024 characters.');
          e.preventDefault();
          e.stopPropagation();
          return false;  
        }

        var data = {title: $('#title').val(), slug: $('#slug').val(), description: $('#description').val(), questions: []};
        $('.question').each(function(index, el){
            var $el = $(el);
            var questionData = {};
            questionData.type = $el.find('input[name="question-type"]').val();
            questionData.message = $el.find('input[name="question-message"]').val();
            questionData.required = $el.find('input[name="question-required"]').is(":checked");
            questionData.order_number = index;
            var choices = [];
            $el.find('input[name="choice-message"]').each(function(choiceIndex, choiceEl){
                var choiceData = {};
                choiceData.message = $(choiceEl).val();
                choiceData.order_number = choiceIndex;
                choices.push(choiceData);
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
                if (data['warnings'].length > 0){
                    alert(data['warnings'].join('\n'));
                }
                if ('url' in data){
                    window.location = data['url'];
                }
            }
        });
    });

    $('.add-preset').live('click', function(e)
    {
      var big_parent = $(this).closest(".question").find(".choices");      
      e.preventDefault();

      $('#preset-form').dialog({ 
          title:'Select Preset',
          resizable:false,
          disabled:true,
          modal:true,
          hide:'fold',
          buttons: 
            {
                "Use Selected": function() 
                {    

                    var preset_name = $('.preset-select').find(":selected").text();
                    $( this ).dialog("close");

                    $.ajax({
                        url: SEARCH_PRESET_URL,
                        type: "get",
                        data: "title=" + preset_name,
                        success: function(data)
                        {
                            var remaining = data['values'].length;
                            big_parent.children('.choice').each(function(index) 
                            {   
                                var opt = $(this).find('input[type=text],textarea,select').filter(':visible:first');
                                if (index < data['values'].length)
                                { 
                                    opt.val( data['values'][index] ); 
                                    remaining--;
                                }
                                else
                                { $(this).remove(); }
                            });
                            for (x = 0; x < remaining; x++)
                            {
                                newChoiceDynamic(big_parent, data['values'][x+(data['values'].length-remaining)]);
                            }
                        },
                    });                                        
                },

                Cancel: function() 
                { $( this ).dialog("close"); }
            },
          close:function(e,ui)
          { $(this).dialog('destroy');}
        });
    });


    $('#new-text-area').click(newTextArea);
    $('#new-text-box').click(newTextBox);
    $('#new-check-boxes').click(newCheckBoxes);
    $('#new-radio-buttons').click(newRadioButtons);
    $('#new-drop-down-list').click(newDropDownList);
    $('.add-choice').live('click', newChoice);
    $('.choice .delete').live('click', removeChoice);
    $('.message .delete').live('click', removeQuestion);
    $(window).scroll(function(){
      $('#toolbox').toggleClass('scrolling', $(window).scrollTop() > $('#toolbox-outer').offset().top);
    });
    initializeSortables()
});


