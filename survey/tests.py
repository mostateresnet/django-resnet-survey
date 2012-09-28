"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from datetime import timedelta
from django.utils.timezone import now
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from survey.models import Survey, Question, Choice, Answer, Ballot


# pylint: disable=R0902
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


class BallotResultsViewTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey")
        self.questionRA = Question.objects.create(message="What time is it", survey=self.survey, type="RA")
        self.choiceRA = Choice.objects.create(question=self.questionRA, message="5 oclock")
        self.questionTB = Question.objects.create(message="Textbox question", survey=self.survey, type="TB")
        self.choiceTB = Choice.objects.create(question=self.questionTB, message="QuestionText")
        self.ballot = Ballot.objects.create(survey=self.survey)

    def test_view(self):
        response = self.client.get(reverse('ballot', kwargs={'slug': self.survey.slug}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_empty_page(self):
        response = self.client.get(reverse('ballot', kwargs={'slug': self.survey.slug, }), {'page': 0}, follow=True)
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
        self.now = now()
        self.one_hour = timedelta(hours=1)

    def test_date_range_makes_survey_active(self):
        self.survey.start_date = self.now - self.one_hour
        self.survey.end_date = self.now + self.one_hour
        self.survey.save()
        self.assertTrue(self.survey.is_active)

    def test_date_range_makes_survey_inactive(self):
        self.survey.start_date = self.now - 2 * self.one_hour
        self.survey.end_date = self.now - self.one_hour
        self.survey.save()
        self.assertFalse(self.survey.is_active)

    def test_date_range_with_no_end_date_makes_survey_active(self):
        self.survey.start_date = self.now - self.one_hour
        self.survey.end_date = None
        self.survey.save()
        self.assertTrue(self.survey.is_active)

    def test_date_range_with_no_end_date_makes_survey_inactive(self):
        self.survey.start_date = self.now + self.one_hour
        self.survey.end_date = None
        self.survey.save()
        self.assertFalse(self.survey.is_active)

    def test_is_active_false_closes_survey(self):
        self.survey.start_date = self.now - 2 * self.one_hour
        self.survey.end_date = self.now - self.one_hour
        self.survey.save()
        response = self.client.get(self.survey_url)
        self.assertIn(u'closed', unicode(response))
        self.assertEqual(response.status_code, 403)

    def test_is_active_false_closes_survey_post(self):
        self.survey.start_date = self.now - 2 * self.one_hour
        self.survey.end_date = self.now - self.one_hour
        self.survey.save()
        response = self.client.post(self.survey_url)
        self.assertIn(u'closed', unicode(response))
        self.assertEqual(response.status_code, 403)

    def test_get_survey(self):
        self.survey.publish()
        response = self.client.get(self.survey_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_survey(self):
        self.survey.publish()
        postdata = {"q" + unicode(self.questionRA.pk): "c" + unicode(self.choiceRA.pk), "q" + unicode(self.questionTB.pk): "word up dawg"}
        response = self.client.post(self.survey_url, postdata)
        self.assertEqual(response.status_code, 200)

    def test_survey_results(self):
        postdata = {"q" + unicode(self.questionRA.pk): "c" + unicode(self.choiceRA.pk), "q" + unicode(self.questionTB.pk): "word up dawg"}
        response = self.client.post(self.survey_url, postdata)
        response = self.client.get(self.survey_results_url)
        self.assertEqual(response.status_code, 200)

    def test_post_survey_empty_post_makes_no_answers(self):
        self.survey.publish()
        response = self.client.post(self.survey_url, {})
        self.assertEqual(Answer.objects.all().count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_post_survey_empty_value_makes_no_answers(self):
        self.survey.publish()
        postdata = {
            u'q%s' % self.questionTB.pk: '',  # Empty value in the textbox
        }
        response = self.client.post(self.survey_url, postdata)
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

    def test_new_survey_adds_survey(self):
        # Needs maor casperjs!
        self.client.get(reverse('newsurvey'))
        data = """
            {
                "title": "Getting to know you",
                "questions": [{
                    "type": "CH",
                    "message": "check",
                    "choices": ["mark", "please", "on the baby"]
                }, {
                    "type": "RA",
                    "message": "radio",
                    "choices": ["FM", "AM"]
                }, {
                    "type": "DD",
                    "message": "drop",
                    "choices": ["stop", "roll"]
                }, {
                    "type": "TB",
                    "message": "cardboard"
                }, {
                    "type": "TA",
                    "message": "area"
                }]
            }
        """
        postdata = {'r': data}
        self.client.post(reverse('newsurvey'), postdata)
        self.assertEqual(Survey.objects.get(slug='getting-to-know-you').title, "Getting to know you")

    def test_survey_publish_publishes_survey(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='admin', password='asdf')
        self.client.get(reverse('publishsurvey', args=[self.survey.slug]))
        self.survey = Survey.objects.get(pk=self.survey.pk)
        self.assertTrue(self.survey.is_active)

    def test_survey_close_closes_survey(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='admin', password='asdf')
        self.client.get(reverse('closesurvey', args=[self.survey.slug]))
        self.survey = Survey.objects.get(pk=self.survey.pk)
        self.assertFalse(self.survey.is_active)
