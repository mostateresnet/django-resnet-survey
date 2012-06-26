"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from survey.models import Survey, Question


class QuestionTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey")
        self.question = Question.objects.create(message="What do you like best?", survey=self.survey)

    def test_unicode(self):
        self.assertTrue(unicode(self.question))


class IndexViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')

    def test_get_index(self):
        Survey.objects.create(title="My new survey", slug="my-new-survey")
        response = self.client.get('', follow=True)
        self.assertEqual(response.status_code, 200)
