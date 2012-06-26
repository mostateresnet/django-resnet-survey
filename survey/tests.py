"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from survey.models import Survey, Question, Choice


class QuestionTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey")
        self.question = Question.objects.create(message="What do you like best?", survey=self.survey)

    def test_unicode(self):
        self.assertTrue(unicode(self.question))


class ChoiceTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey")
        self.question = Question.objects.create(message="What do you like best?", survey=self.survey)
        self.choice = Choice.objects.create(question=self.question, message="Word up dog")

    def test_unicode(self):
        self.assertTrue(unicode(self.choice))


class IndexViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')

    def test_get_index(self):
        Survey.objects.create(title="My new survey", slug="my-new-survey")
        response = self.client.get('', follow=True)
        self.assertEqual(response.status_code, 200)


class SurveyViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey")
        self.question = Question.objects.create(message="What time is it", survey=self.survey)
        self.choice = Choice.objects.create(question=self.question, message="5 oclock")
        self.question2 = Question.objects.create(message="Textbox question", survey=self.survey)
        self.choice2 = Choice.objects.create(question=self.question2, message="QuestionText")

    def test_get_survey(self):
        response = self.client.get("/my-new-survey", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_survey(self):
        postdata = {"q" + unicode(self.question.pk): "c" + unicode(self.choice.pk), "q" + unicode(self.question2.pk): "word up dawg"}
        response = self.client.post("/my-new-survey", postdata)
        self.assertEqual(response.status_code, 200)
