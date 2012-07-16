from django.db import models
from django.utils.timezone import now


class Survey(models.Model):
    """
    Survey model has a set of questions.
    """
    title = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=1024, primary_key=True)
    is_active = models.BooleanField(default=True)

    @models.permalink
    def get_absolute_url(self):
        return ('survey', (), {'slug': self.slug})

    def __unicode__(self):
        return self.title


class Question(models.Model):
    """
    A Question is associated with a Survey and its type can be: textbox, textarea, checkbox, radio, or dropdown.
    """
    survey = models.ForeignKey('Survey')
    message = models.CharField(max_length=1024)

    QUESTION_TYPES = (
        ('TB', 'textbox'),
        ('TA', 'textarea'),
        ('CH', 'checkbox'),
        ('RA', 'radio'),
        ('DD', 'dropdown'),
    )
    type = models.CharField(max_length=2, choices=QUESTION_TYPES)

    def answer_with_text(self, text):
        if text:
            choice = self.choice_set.all()[0]
            Answer.objects.create(choice=choice, text=text)

    def answer_with_choices(self, choices):
        for choice in choices:
            Answer.objects.create(choice=choice, text=unicode(choice.pk))

    def __unicode__(self):
        return self.message


class Choice(models.Model):
    """
    A Choice is an answer that can be picked as part of a question.
    """
    question = models.ForeignKey('Question')
    message = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.message


class Answer(models.Model):
    """
    Answer contains the choice that the user has picked as their answer.
    """
    choice = models.ForeignKey('Choice')
    text = models.CharField(max_length=1024)
    datetime = models.DateTimeField(default=now)

    def __unicode__(self):
        return self.text
