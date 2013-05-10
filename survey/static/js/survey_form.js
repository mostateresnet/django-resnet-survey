function removeQuestion(e){
    $removableDiv = $(e.currentTarget).closest('.question');
    
    if ($removableDiv.is('.question-group *') && $removableDiv.siblings('.question').length < 1){
        if (confirm('Are you sure you want to delete this group of questions?'))
            $removableDiv.closest('.question-group').remove()
        return;
    }
        
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

function addQuestionToElement(element, question){
    element.append(question);
    question.find('[placeholder]').blur();
    initializeSortables();
}

function newQuestionHandler(questionType){
    return function(){
        var $question = $(QUESTION_SOURCES[questionType]);
        addQuestionToElement($('#questions'), $question);
    };
}

function addQuestionToGroup(){
    var $question = $(QUESTION_SOURCES['IG']);
    addQuestionToElement($(this).closest('.question-options').siblings('.questions'), $question);
}

function initializeSortables(){
    $(".questions").sortable({
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
var newLikertScale = newQuestionHandler('LS');


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

        var data = {title: $('#title').val(), description: $('#description').val(), questions: [], groups: []};
        $('.question').each(function(index, el){
            var $el = $(el);

            if ($el.is('.question-group *'))
                /* Ignore any questions that are part of a group -- we'll handle them later */
                return;

            var questionData = {};
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
            questionData.type = $el.find('input[name="question-type"]').val();
            questionData.required = $el.find('input[name="question-required"]').is(":checked");
            if ($el.is('.question-group')){                
                questionData.group = index;
                
                data.groups.push( { index: index, message: $el.parent().find('input[name="likert-message"]').val() } );
                
                $el.find('.question').each(function(groupMemberIndex, groupMemberEl){
                    var groupMemberData = $.extend({}, questionData);
                    groupMemberData.message = $(groupMemberEl).find('input[name="question-message"]').val();
                    groupMemberData.order_number = groupMemberIndex + index;
                    data.questions.push(groupMemberData);
                });
            }
            else {
                questionData.message = $el.find('input[name="question-message"]').val();
                questionData.order_number = index;
                data.questions.push(questionData);
            }
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
    $('#new-likert-scale').click(newLikertScale);
    $('.add-question-to-group').live('click', addQuestionToGroup);
    $('.add-choice').live('click', newChoice);
    $('.choice .delete').live('click', removeChoice);
    $('.message .delete').live('click', removeQuestion);
    $(window).scroll(function(){
      $('#toolbox').toggleClass('scrolling', $(window).scrollTop() > $('#toolbox-outer').offset().top);
    });
    initializeSortables()
});


