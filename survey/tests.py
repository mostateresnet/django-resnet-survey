"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
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
        response = self.client.get(reverse('index'), follow=True)
        self.assertEqual(response.status_code, 200)


class SurveyViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey")
        self.survey_url = self.survey.get_absolute_url()
        self.survey_results_url = reverse('surveyresults', kwargs={'slug': self.survey.slug})
        self.questionRA = Question.objects.create(message="What time is it", survey=self.survey, type="RA")
        self.choiceRA = Choice.objects.create(question=self.questionRA, message="5 oclock")
        self.questionTB = Question.objects.create(message="Textbox question", survey=self.survey, type="TB")
        self.choiceTB = Choice.objects.create(question=self.questionTB, message="QuestionText")

    def test_is_active_false_closes_survey(self):
        self.survey.is_active = False
        self.survey.save()
        response = self.client.post(self.survey_url)
        self.assertIn(u'closed', unicode(response))
        self.assertEqual(response.status_code, 403)

    def test_get_survey(self):
        response = self.client.get(self.survey_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_survey(self):
        postdata = {"q" + unicode(self.questionRA.pk): "c" + unicode(self.choiceRA.pk), "q" + unicode(self.questionTB.pk): "word up dawg"}
        response = self.client.post(self.survey_url, postdata)
        self.assertEqual(response.status_code, 200)

    def test_survey_results(self):
        postdata = {"q" + unicode(self.questionRA.pk): "c" + unicode(self.choiceRA.pk), "q" + unicode(self.questionTB.pk): "word up dawg"}
        response = self.client.post(self.survey_url, postdata)
        response = self.client.get(self.survey_results_url)
        self.assertEqual(response.status_code, 200)

    def test_post_survey_empty_post_makes_no_answers(self):
        response = self.client.post(self.survey_url, {})
        self.assertEqual(Answer.objects.all().count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_post_survey_bad_choice_ignores_it(self):
        postdata = {
            u'q%s' % self.questionRA.pk: 'c328947293847',
        }
        self.client.post(self.survey_url, postdata)
        self.assertEqual(Answer.objects.all().count(), 0)

    def test_post_survey_choice_for_wrong_question_ignores_it(self):
        postdata = {
            u'q%s' % self.questionRA.pk: 'c%s' % self.choiceTB.pk,  # choiceTB belongs to questionTB, not question 1!
        }
        self.client.post(self.survey_url, postdata)
        self.assertEqual(Answer.objects.all().count(), 0)

    def test_post_survey_text_answer_for_multichoice_ignores_it(self):
        postdata = {
            u'q%s' % self.questionRA.pk: 'I love pizza.',  # questionRA has radio buttons!
        }
        self.client.post(self.survey_url, postdata)
        self.assertEqual(Answer.objects.all().count(), 0)
