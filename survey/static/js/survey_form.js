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
    $this = $(e.currentTarget);
    var $last_choice = $this.parent().siblings('.choice').last()
    var $choice = $last_choice.clone();
    $last_choice.after($choice);
    $choice.find('input').val('').blur();
}

function newQuestionHandler(questionType){
    return function(){
        var $question = $(QUESTION_SOURCES[questionType]);
        $('#survey-form').append($question);
        $question.find('[placeholder]').blur();
    };
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
                if ('error' in data){
                    alert(data['error']);
                }
                else{
                    window.location = data['url'];
                }
            }
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
});
