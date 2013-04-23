"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.unittest import SkipTest
from survey.models import Survey, Question, Choice, Answer, Ballot, Preset, PresetChoice
from survey.helpers import now, get_current_timezone
try:
    from django.utils.timezone import utc
except ImportError:
    utc = None


# pylint: disable=R0902
class QuestionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey", creator=self.user)
        self.question = Question.objects.create(message="What do you like best?", survey=self.survey)

    def test_unicode(self):
        self.assertTrue(unicode(self.question))


class ChoiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey", creator=self.user)
        self.question = Question.objects.create(message="What do you like best?", survey=self.survey)
        self.choice = Choice.objects.create(question=self.question, message="Word up dog")

    def test_unicode(self):
        self.assertTrue(unicode(self.choice))


class IndexViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')

    def test_get_index(self):
        Survey.objects.create(title="My new survey", slug="my-new-survey", creator=self.user)
        response = self.client.get(reverse('index'), follow=True)
        self.assertEqual(response.status_code, 200)


class BallotResultsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey", creator=self.user)
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

    def test_no_ballots_shows_no_ballots(self):
        self.ballot.delete()
        response = self.client.get(reverse('ballot', kwargs={'slug': self.survey.slug}), follow=True)
        self.assertIsNone(response.context['ballot'])
        self.assertIsNone(response.context['next_ballot'])
        self.assertIsNone(response.context['previous_ballot'])

    def test_get_ballot_or_404(self):
        response = self.client.get(reverse('ballot', kwargs={'slug': self.survey.slug, 'ballot_id': 123456789}), follow=True)
        self.assertEqual(response.status_code, 404)


class SurveyViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey", creator=self.user)
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
        self.client.logout()
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
            {"title":"a new survey for post data",
            "slug":"post-data-survey",
            "description":"fdsasdf",
            "questions":[
                {"type":"DD",
                "message":"ddl",
                "required":false,
                "order_number":0,
                "choices":[
                    {"message":"1","order_number":0},
                    {"message":"2","order_number":1}
                ]}
            ]}
        """
        postdata = {'r': data}
        self.client.post(reverse('newsurvey'), postdata)
        self.assertEqual(Survey.objects.get(slug='post-data-survey').title, "a new survey for post data")

    def test_new_survey_unique_slug(self):
        data = """
            {"title":"a new survey for post data",
            "slug":"my-new-survey",
            "description":"fdsasdf",
            "questions":[
                {"type":"DD",
                "message":"ddl",
                "required":false,
                "order_number":0,
                "choices":[
                    {"message":"1","order_number":0},
                    {"message":"2","order_number":1}
                ]}
            ]}
        """
        postdata = {'r': data}
        response = self.client.post(reverse('newsurvey'), postdata)
        response_data = json.JSONDecoder().decode(response.content)
        self.assertIn(
            'That title is already taken. Please choose a different one.',
            response_data['warnings'],
            'Integrity error: slug uniqueness is not being inforced')


class SurveyEditViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="Text Only Survey", slug="text-only-survey", creator=self.user)
        self.survey2 = Survey.objects.create(title="Text Only Survey", slug="survey", creator=self.user)
        self.arbitrary_start_date_str = 'Mon, 01 Jan 2013 06:00:00 GMT'
        self.arbitrary_start_date = datetime.strptime(self.arbitrary_start_date_str, '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=utc)
        self.preset = Preset.objects.create(title="States")
        PresetChoice.objects.create(preset=self.preset, option="MO")

    def test_get_context_data(self):
        response = self.client.get(reverse('surveyedit', args=[self.survey.slug]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = """
            {
                "title":"Text Only Survey",
                "slug":"text-onlysurvey",
                "description":"",
                "questions":
                [
                    {
                        "type":"TA",
                        "message":"Text Area Question",
                        "required":false,
                        "order_number":0
                    },
                    {
                        "type":"TB",
                        "message":"Text Box Question",
                        "required":false,
                        "order_number":1
                    },
                    {
                        "type":"CH",
                        "message":"Check Box Question",
                        "required":false,
                        "order_number":2,
                        "choices":
                        [
                            {
                                "message":"Check Box Choice 1",
                                "order_number":0
                            },
                            {
                                "message":"Check Box Choice 2",
                                "order_number":1
                            },
                            {
                                "message":"Check Box Choice 3",
                                "order_number":2
                            }
                        ]
                    },
                    {
                        "type":"RA",
                        "message":"Radio Button Question",
                        "required":false,
                        "order_number":3,
                        "choices":
                        [
                            {
                                "message":"Radio Choice 1",
                                "order_number":0
                            },
                            {
                                "message":"Radio Choice 2",
                                "order_number":1
                            },
                            {
                                "message":"Radio Choice 3",
                                "order_number":2
                            }
                        ]
                    },
                    {
                        "type":"DD",
                        "message":"Drop Down List Question",
                        "required":false,
                        "order_number":4,
                        "choices":
                        [
                            {
                                "message":"Drop Down Choice 1",
                                "order_number":0
                            },
                            {
                                "message":"Drop Down Choice 2",
                                "order_number":1
                            },
                            {
                                "message":"Drop Down Choice 3",
                                "order_number":2
                            }
                        ]
                    }
                ]
            }
        """
        postdata = {'r': data}
        response = self.client.post(reverse('surveyedit', args=[self.survey.slug]), postdata)
        self.assertEqual(response.status_code, 200, "The page didn't return a 200")
        self.assertEqual(self.survey.title, 'Text Only Survey', "The Survey didn't update properly")
        self.assertEqual(self.survey.question_set.all()[0].message, 'Text Area Question', "Question didn't update properly")
        self.assertEqual(self.survey.question_set.all()[2].choice_set.all()[1].message, 'Check Box Choice 2', "Question Order is broken")
        self.assertEqual(self.survey.question_set.all()[4].choice_set.all()[2].order_number, 2, "Choice Order is broken")

    def test_has_access(self):
        self.survey.start_date = self.arbitrary_start_date
        self.survey.save()

        data = """
            {
                "title":"Text Only Survey",
                "slug":"survey",
                "description":"",
                "questions":
                [
                    {
                        "type":"TA",
                        "message":"Text Area Question",
                        "required":false,
                        "order_number":0
                    }
                ]
            }
        """
        postdata = {'r': data}
        response = self.client.post(reverse('surveyedit', args=[self.survey.slug]), postdata)
        self.assertEqual(response.status_code, 404, "The page didn't return a 404")

    def test_survey_slug_unique(self):
        data = """
            {
                "title":"Text Only Survey",
                "slug":"survey",
                "description":"",
                "questions":
                [
                    {
                        "type":"TA",
                        "message":"Text Area Question",
                        "required":false,
                        "order_number":0
                    }
                ]
            }
        """
        postdata = {'r': data}
        response = self.client.post(reverse('surveyedit', args=[self.survey.slug]), postdata)
        response_data = json.JSONDecoder().decode(response.content)
        self.assertIn(
            'That title is already taken. Please choose a different one.',
            response_data['warnings'],
            'Integrity error: slug uniqueness is not being inforced')

    def test_survey_slug_or_title_required(self):
        data = """
            {
                "title":"",
                "slug":"",
                "description":"",
                "questions":
                [
                    {
                        "type":"TA",
                        "message":"Text Area Question",
                        "required":false,
                        "order_number":0
                    }
                ]
            }
        """
        postdata = {'r': data}
        response = self.client.post(reverse('surveyedit', args=[self.survey.slug]), postdata)
        response_data = json.JSONDecoder().decode(response.content)
        self.assertIn('Please enter a valid title.', response_data['warnings'], 'Integrity error: slug must be defined')


class SurveyResultsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="Text Only Survey", slug="text-only-survey", creator=self.user)
        self.question1 = Question.objects.create(survey=self.survey, message="Question1(CH)", type="CH", required=False, order_number=0)
        self.choice1 = Choice.objects.create(question=self.question1, message="Q1C1", order_number=0)
        self.choice2 = Choice.objects.create(question=self.question1, message="Q1C2", order_number=1)
        self.choice3 = Choice.objects.create(question=self.question1, message="Q1C2", order_number=2)
        self.question2 = Question.objects.create(survey=self.survey, message="Question(RA)", type="RA", required=False, order_number=1)
        self.choice4 = Choice.objects.create(question=self.question2, message="Q2C1", order_number=0)
        self.choice5 = Choice.objects.create(question=self.question2, message="Q2C2", order_number=1)
        self.choice6 = Choice.objects.create(question=self.question2, message="Q2C2", order_number=2)
        self.ballot1 = Ballot.objects.create(survey=self.survey)
        self.ballot2 = Ballot.objects.create(survey=self.survey)
        self.ballot3 = Ballot.objects.create(survey=self.survey)
        self.question1.answer_with_choices((self.choice1, self.choice2, self.choice3), self.ballot1)
        self.question2.answer_with_choices((self.choice4,), self.ballot1)
        self.question1.answer_with_choices((self.choice1, self.choice2), self.ballot2)
        self.question2.answer_with_choices((self.choice4,), self.ballot2)
        self.question1.answer_with_choices((self.choice1,), self.ballot3)
        self.question2.answer_with_choices((self.choice4,), self.ballot3)

    def test_get_context_data(self):
        response = self.client.get(reverse('surveyresults', args=[self.survey.slug, self.choice1.pk]))
        self.assertEqual(response.status_code, 200, "The page didn't return a 200")


class SurveyDetailsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey", creator=self.user)
        self.arbitrary_start_date_str = 'Tue, 01 Jan 2013 11:00:00 GMT'
        self.arbitrary_start_date = datetime.strptime(self.arbitrary_start_date_str, '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=utc)
        self.arbitrary_end_date_str = 'Wed, 01 Jan 2020 11:00:00 GMT'
        self.arbitrary_end_date = datetime.strptime(self.arbitrary_end_date_str, '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=utc)

    def test_set_start_and_end_dates(self):
        if self.arbitrary_start_date.tzinfo:
            self.arbitrary_start_date = self.arbitrary_start_date.astimezone(get_current_timezone())
        if self.arbitrary_end_date.tzinfo:
            self.arbitrary_end_date = self.arbitrary_end_date.astimezone(get_current_timezone())
        post_data = {
            'start_date': self.arbitrary_start_date.strftime('%m/%d/%Y'),
            'start_time': self.arbitrary_start_date.strftime('%I:%M%p'),
            'end_date': self.arbitrary_end_date.strftime('%m/%d/%Y'),
            'end_time': self.arbitrary_start_date.strftime('%I:%M%p'),
            'set_duration': '',
        }

        self.client.post(reverse('surveydetails', args=[self.survey.slug]), post_data)
        self.survey = Survey.objects.get(slug="my-new-survey")
        self.assertEqual(self.survey.start_date, self.arbitrary_start_date)
        self.assertEqual(self.survey.end_date, self.arbitrary_end_date)

    def test_set_social(self):
        self.client.post(reverse('surveydetails', args=[self.survey.slug]), {'show_social': True})
        self.survey = Survey.objects.get(slug="my-new-survey")
        self.assertEqual(self.survey.show_social, False)

    def test_set_track(self):
        self.client.post(reverse('surveydetails', args=[self.survey.slug]), {'disable_cookies': True})
        self.survey = Survey.objects.get(slug="my-new-survey")
        self.assertEqual(self.survey.use_cookies, False)

    def test_blank_dates(self):
        response = self.client.post(reverse('surveydetails', args=[self.survey.slug]), {'start_date': '', 'start_time': '',
                                                                                        'end_date': '', 'end_time': '', 'set_duration': ''})
        self.assertEqual(response.status_code, 200, "This page should return a 200")
        self.assertEqual(self.survey.start_date, None)

    def test_valid_date_values(self):
        response = self.client.post(reverse('surveydetails', args=[self.survey.slug]), {'start_date': '01/01/2011', 'start_time': '',
                                                                                        'end_date': '', 'end_time': '', 'set_duration': ''})

    def test_def_get(self):
        response = self.client.get(reverse('surveydetails', args=[self.survey.slug]))
        self.assertEqual(response.status_code, 404, "The page didn't return a 404")

    def test_survey_change_publish_date_after_gone_live(self):
        ballot1 = Ballot.objects.create(survey=self.survey)
        self.survey.start_date = self.arbitrary_start_date
        self.survey.save()
        response = self.client.post(reverse('surveydetails', args=[self.survey.slug]), {'start_date': '01/01/2013', 'start_time': '12:01am',
                                                                                        'end_date': '01/01/2020', 'end_time': '12:00am', 'set_duration': ''})
        response_data = json.JSONDecoder().decode(response.content)
        self.assertEqual(response.status_code, 200, "This page should return a 200")
        self.assertEqual(response_data['errors'][0], "A surveys publish date cannot be changed if it has already gone live.",
                         "Error: Survey publish dates are being allowed to change once ballots are present")


class SurveyDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey", creator=self.user)

    def test_post(self):
        response = self.client.post(reverse('surveydelete', args=[self.survey.slug]))


class SurveyCloneViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey", creator=self.user)
        self.question1 = Question.objects.create(survey=self.survey, message="Question1(CH)", type="CH", required=False, order_number=0)
        self.choice1 = Choice.objects.create(question=self.question1, message="Q1C1", order_number=0)
        self.choice2 = Choice.objects.create(question=self.question1, message="Q1C2", order_number=1)

    def test_post_non_unique_slug(self):
        response = self.client.post(reverse('surveyclone', args=[self.survey.slug]), {'title': 'My new survey'})
        response_data = json.JSONDecoder().decode(response.content)
        self.assertEqual(response.status_code, 200, "This request should return a 200")
        self.assertEqual(response_data['error'], 'A survey with that title already exists.', 'Unique slugs are not being enforced')

    def test_post_unique_slug(self):
        response = self.client.post(reverse('surveyclone', args=[self.survey.slug]), {'title': 'food survey'})
        response_data = json.JSONDecoder().decode(response.content)
        self.assertEqual(response.status_code, 200, "This request should return a 200")
        self.assertEqual(response_data['status'], 'success', 'The procedure did not succeed')

    def test_post_not_auth_user(self):
        self.user.is_staff = False
        self.user.save()
        response = self.client.post(reverse('surveyclone', args=[self.survey.slug]), {'title': 'My new survey'})
        response_data = json.JSONDecoder().decode(response.content)
        self.assertEqual(response.status_code, 200, "This request should return a 200")
        self.assertEqual(response_data['status'], 'Auth Error', 'The should return an Auth Error')


class SurveyQRCodeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="My new survey", slug="my-new-survey", creator=self.user)

    def test_get(self):
        try:
            response = self.client.get(reverse('qrcode', args=[self.survey.slug]))
            self.assertEqual(response.status_code, 200, "This request should return a 200")
        except ImportError:
            raise SkipTest("QRCode testing requires the qrcode library")


class SurveyExportViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='admin', password='asdf')
        self.survey = Survey.objects.create(title="Text Only Survey", slug="text-only-survey", creator=self.user)
        self.question1 = Question.objects.create(survey=self.survey, message="Question1(CH)", type="CH", required=False, order_number=0)
        self.choice1 = Choice.objects.create(question=self.question1, message="Q1C1", order_number=0)
        self.choice2 = Choice.objects.create(question=self.question1, message="Q1C2", order_number=1)
        self.choice3 = Choice.objects.create(question=self.question1, message="Q1C2", order_number=2)
        self.question2 = Question.objects.create(survey=self.survey, message="Question(RA)", type="RA", required=False, order_number=1)
        self.choice4 = Choice.objects.create(question=self.question2, message="Q2C1", order_number=0)
        self.choice5 = Choice.objects.create(question=self.question2, message="Q2C2", order_number=1)
        self.choice6 = Choice.objects.create(question=self.question2, message="Q2C2", order_number=2)
        self.question3 = Question.objects.create(survey=self.survey, message="Question(TB)", type="TB", required=False, order_number=2)
        self.choice7 = Choice.objects.create(question=self.question3, message="Q3C1", order_number=0)
        self.ballot1 = Ballot.objects.create(survey=self.survey)
        self.ballot2 = Ballot.objects.create(survey=self.survey)
        self.ballot3 = Ballot.objects.create(survey=self.survey)
        self.ballot4 = Ballot.objects.create(survey=self.survey)
        self.question1.answer_with_choices((self.choice1, self.choice2, self.choice3), self.ballot1)
        self.question2.answer_with_choices((self.choice4,), self.ballot1)
        self.question1.answer_with_choices((self.choice1, self.choice2), self.ballot2)
        self.question2.answer_with_choices((self.choice4,), self.ballot2)
        self.question1.answer_with_choices((self.choice1,), self.ballot3)
        self.question2.answer_with_choices((self.choice4,), self.ballot3)
        self.question3.answer_with_text((self.choice7,), self.ballot4)

    def test_get_full_report(self):
        response = self.client.get(reverse('exportresults', args=[self.survey.slug]), {'rtype': 'Full'})
        self.assertEqual(response.status_code, 200, "This request should return a 200")

    def test_get_summary_report(self):
        response = self.client.get(reverse('exportresults', args=[self.survey.slug]), {'rtype': 'Summary'})
        self.assertEqual(response.status_code, 200, "This request should return a 200")

    def test_no_report_type_selected(self):
        response = self.client.get(reverse('exportresults', args=[self.survey.slug]))
        self.assertEqual(response.status_code, 200, "This request should return a 200")

    def test_user_not_staff(self):
        self.user.is_staff = False
        self.user.save()
        response = self.client.get(reverse('exportresults', args=[self.survey.slug]))
        self.assertEqual(response.status_code, 403, "This request should return a 403")


class PresetSearchView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', email="a@a.com", password='asdf')
        self.client.login(username='admin', password='asdf')
        self.preset = Preset.objects.create(title="States")
        PresetChoice.objects.create(preset=self.preset, option="MO")

    def test_get(self):
        response = self.client.get(reverse('preset_search_view'), {'title': 'States'})
        self.assertEqual(response.status_code, 200, "This request should return a 200")
