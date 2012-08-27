from django.conf.urls import patterns, url
from survey.views import IndexView, SurveyView, SurveyResultsView, SurveyNewView, BallotResultsView

# pylint: disable-msg=C0103,E1120
urlpatterns = patterns(
    'survey.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^new/$', SurveyNewView.as_view(), name='newsurvey'),
    url(r'^(?P<slug>[-_\w]+)/$', SurveyView.as_view(), name='survey'),
    url(r'^(?P<slug>[-_\w]+)/edit/$', SurveyView.as_view(), name='editsurvey'),
    url(r'^(?P<slug>[-_\w]+)/results/$', SurveyResultsView.as_view(), name='surveyresults'),
    url(r'^(?P<slug>[-_\w]+)/ballots/$', BallotResultsView.as_view(), name='ballot'),
)
