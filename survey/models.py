from django.db import models
import datetime as dt


class Survey(models.Model):
    """
    Survey model has a set of questions.
    """
    title = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=1024, primary_key=True)
    is_active = models.BooleanField(default=True)


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


class Choice(models.Model):
    """
    A Choice is an answer that can be picked as part of a question.
    """
    question = models.ForeignKey('Question')
    message = models.CharField(max_length=1024)


class Answer(models.Model):
    """
    Answer contains the choice that the user has picked as their answer.
    """
    choice = models.ForeignKey('Choice')
    text = models.CharField(max_length=1024)
    datetime = models.DateTimeField(default=dt.datetime.now)
