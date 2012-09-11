from django.conf.urls import patterns, url
from survey.views import IndexView, SurveyView, SurveyResultsView, SurveyNewView, SurveyEditView, BallotResultsView, SurveyPublishView, SurveyQRCodeView

# pylint: disable-msg=C0103,E1120
urlpatterns = patterns(
    'survey.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^new/$', SurveyNewView.as_view(), name='newsurvey'),
    url(r'^(?P<slug>[-_\w]+)/$', SurveyView.as_view(), name='survey'),
    url(r'^(?P<slug>[-_\w]+)/edit/$', SurveyEditView.as_view(), name='editsurvey'),
    url(r'^(?P<slug>[-_\w]+)/publish/$', SurveyPublishView.as_view(), name='publishsurvey'),
    url(r'^(?P<slug>[-_\w]+)/results/$', SurveyResultsView.as_view(), name='surveyresults'),
    url(r'^(?P<slug>[-_\w]+)/ballots/$', BallotResultsView.as_view(), name='ballot'),
    url(r'^(?P<slug>[-_\w]+)/qrcode/$', SurveyQRCodeView.as_view(), name='qrcode'),
)
