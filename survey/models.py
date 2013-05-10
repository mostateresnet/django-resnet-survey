from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from collections import defaultdict
from survey.helpers import now, get_current_timezone


class Survey(models.Model):
    """
    Survey model has a set of questions.
    """
    title = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=1024, unique=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=1024, null=False, blank=True)
    use_cookies = models.BooleanField(default=True)
    creator = models.ForeignKey(User, related_name="+")
    show_social = models.BooleanField(default=True)

    @models.permalink
    def get_absolute_url(self):
        return ('survey', (), {'slug': self.slug})

    class AlreadyPublishedError(Exception):
        pass

    @property
    def is_active(self):
        end_date = self.end_date
        if self.start_date:
            return self.start_date <= now() and (not end_date or now() <= end_date)
        return False

    def clone(self, other):
        groups = defaultdict(QuestionGroup.objects.create)
        groups[None] = None
        # copy the questions
        for question in self.question_set.all():
            choice_set = question.choice_set.all()
            new_question = question
            new_question.id = None
            new_question.survey = other
            new_question.group = groups[question.group]
            new_question.save()
            # copy the choices
            for choice in choice_set:
                new_choice = choice
                new_choice.id = None
                new_choice.question = new_question
                new_choice.save()

    @property
    def closed(self):
        return self.end_date and self.end_date <= now()

    @property
    def is_unpublished(self):
        return not self.is_active and not self.closed

    def track(self, on=True):
        self.use_cookies = on
        self.save()

    def social(self, on=True):
        self.show_social = on
        self.save()

    def publish(self, dt=None):
        if dt is None:
            dt = now()
        self.start_date = dt
        self.save()

    def close(self, dt=None):
        if dt is None:
            dt = now()
        self.end_date = dt
        self.save()

    def set_date(self, field, dtStr, tmStr):
        if dtStr == "":
            setattr(self, field, None)
            self.save()
            return
        try:
            dt = datetime.strptime(dtStr + " " + tmStr, '%m/%d/%Y %I:%M%p').replace(tzinfo=get_current_timezone())
            if field == 'start_date' and self.start_date:
                if self.start_date != dt and self.start_date < now() and self.has_results:
                    raise self.AlreadyPublishedError

        except ValueError:
            dt = datetime.strptime(dtStr, '%m/%d/%Y').replace(tzinfo=get_current_timezone())
        setattr(self, field, dt)
        self.save()

    @property
    def has_results(self):
        return self.ballot_set.all().count() > 0

    def __unicode__(self):
        return self.title

    @property
    def cookie(self):
        """
            returns a cookie friendly name
        """
        return str(self.slug.replace('-', '') + 'ballotcookie')

    def add_questions(self, questions, groups):
        """
        Accepts a list of dictionaries containing question data.
        """
        group_dict = defaultdict(QuestionGroup.objects.create)
        group_dict[None] = None
        
        for question_data in questions:
            question = Question.objects.create(
                survey=self,
                message=question_data.get('message', ''),
                type=question_data.get('type', ''),
                required=question_data.get('required'),
                order_number=question_data.get('order_number', 0),
                group=group_dict[question_data.get('group')],
            )
            for choice in question_data.get('choices', []):
                Choice.objects.create(question=question, message=choice.get('message', ''), order_number=choice.get('order_number', 0))

        for group_data in groups:
            group = group_dict[group_data['index']]
            group.message = group_data['message']
            group.save()
            
            
        

class QuestionGroup(models.Model):
    """
    A QuestionGroup is a way to keep track of Questions associated with each other (mostly just used for Likert scales).
    """
    message = models.CharField(max_length=1024, blank=True)

    def __unicode__(self):
        return self.message


class Question(models.Model):
    """
    A Question is associated with a Survey and its type can be: textbox, textarea, checkbox, radio, or dropdown.
    """
    survey = models.ForeignKey('Survey')
    message = models.CharField(max_length=1024)
    group = models.ForeignKey('QuestionGroup', null=True, blank=True)
    required = models.BooleanField(default=False)
    order_number = models.PositiveIntegerField(default=0)

    # DO NOT change the display name for these types - the css depends on them
    QUESTION_TYPES = (
        ('TB', 'textbox'),
        ('TA', 'textarea'),
        ('CH', 'checkbox'),
        ('RA', 'radio'),
        ('DD', 'dropdown'),
    )
    type = models.CharField(max_length=2, choices=QUESTION_TYPES)

    class Meta:
        ordering = ['order_number']

    def answer_with_text(self, text, ballot):
        if text:
            choice = Choice.objects.create(question=self, message=text)
            Answer.objects.create(choice=choice, ballot=ballot)

    def answer_with_choices(self, choices, ballot):
        for choice in choices:
            Answer.objects.create(choice=choice, ballot=ballot)

    def __unicode__(self):
        return self.message


class Choice(models.Model):
    """
    A Choice is an answer that can be picked as part of a question.
    """
    question = models.ForeignKey('Question')
    message = models.CharField(max_length=1024)
    order_number = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order_number']

    def __unicode__(self):
        return self.message


class Answer(models.Model):
    """
    Answer contains the choice that the user has picked as their answer.
    """
    choice = models.ForeignKey('Choice')
    ballot = models.ForeignKey('Ballot', null=True)

    def __unicode__(self):
        return self.choice.message


class Ballot(models.Model):
    """
    Holds a set of Answers so they may be grouped.
    """
    ip = models.IPAddressField(default='127.0.0.1')
    datetime = models.DateTimeField(default=now)
    survey = models.ForeignKey('Survey', null=True)

    def question_list(self):
        """
        Returns a list of question tuples and their associated choices and ballot answers (if any)
        """
        question_list = []
        for question in self.survey.question_set.all():
            choice_list = []
            for choice in question.choice_set.all():
                try:
                    answer = choice.answer_set.get(ballot=self)
                except Answer.DoesNotExist:
                    answer = None
                choice_list.append((choice, answer))
            question_tuple = (question, choice_list)
            question_list.append(question_tuple)
        return question_list

    def answer_list(self):
        """
        Returns a list of answers
        """
        answer_list = []
        for question in self.survey.question_set.all():
            answer = self.answer_set.filter(choice__question=question).values_list('choice__message', flat=True)
            answer_list.append(answer)
        return answer_list


class Preset(models.Model):
    """
    Contains a list of preset choices, i.e. states, timezones, etc...
    """
    title = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.title


class PresetChoice(models.Model):
    """
    An individual preset string
    """
    option = models.CharField(max_length=1024)
    preset = models.ForeignKey('Preset')

    def __unicode__(self):
        return self.option
