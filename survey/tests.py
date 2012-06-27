"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from survey.models import Survey, Question, Choice, Answer


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
        self.question = Question.objects.create(message="What time is it", survey=self.survey, type="RA")
        self.choice = Choice.objects.create(question=self.question, message="5 oclock")
        self.question2 = Question.objects.create(message="Textbox question", survey=self.survey, type="TB")
        self.choice2 = Choice.objects.create(question=self.question2, message="QuestionText")

    def test_is_active_false_closes_survey(self):
        self.survey.is_active = False
        self.survey.save()
        response = self.client.post("/my-new-survey")
        self.assertIn(u'closed', unicode(response))
        self.assertEqual(response.status_code, 403)

    def test_get_survey(self):
        response = self.client.get("/my-new-survey", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_survey(self):
        postdata = {"q" + unicode(self.question.pk): "c" + unicode(self.choice.pk), "q" + unicode(self.question2.pk): "word up dawg"}
        response = self.client.post("/my-new-survey", postdata)
        self.assertEqual(response.status_code, 200)

    def test_post_survey_empty_post_makes_no_answers(self):
        response = self.client.post("/my-new-survey", {})
        self.assertEqual(Answer.objects.all().count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_post_survey_bad_choice_ignores_it(self):
        postdata = {
            u'q%s' % self.question.pk: 'c328947293847',
        }
        self.client.post("/my-new-survey", postdata)
        self.assertEqual(Answer.objects.all().count(), 0)

    def test_post_survey_choice_for_wrong_question_ignores_it(self):
        postdata = {
            u'q%s' % self.question.pk: 'c%s' % self.choice2.pk,  # choice2 belongs to question2, not question 1!
        }
        self.client.post("/my-new-survey", postdata)
        self.assertEqual(Answer.objects.all().count(), 0)

    def test_post_survey_text_answer_for_multichoice_ignores_it(self):
        postdata = {
            u'q%s' % self.question.pk: 'I love pizza.',  # question 1 has radio buttons!
        }
        self.client.post("/my-new-survey", postdata)
        self.assertEqual(Answer.objects.all().count(), 0)
