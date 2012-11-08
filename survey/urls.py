from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from survey.views import *

# pylint: disable-msg=C0103,E1120
urlpatterns = patterns(
    'survey.views',
    url(r'^$', login_required(IndexView.as_view()), name='index'),
    url(r'^new/$', login_required(SurveyNewView.as_view()), name='newsurvey'),
    url(r'^(?P<slug>[-_\w]+)/$', SurveyView.as_view(), name='survey'),
    url(r'^(?P<slug>[-_\w]+)/edit/$', login_required(SurveyEditView.as_view()), name='surveyedit'),
    url(r'^(?P<slug>[-_\w]+)/publish/$', login_required(SurveyPublishView.as_view()), name='publishsurvey'),
    url(r'^(?P<slug>[-_\w]+)/close/$', login_required(SurveyCloseView.as_view()), name='closesurvey'),
    url(r'^(?P<slug>[-_\w]+)/track/$', login_required(SurveyTrackView.as_view()), name='surveytrack'),
    url(r'^(?P<slug>[-_\w]+)/results/$', login_required(SurveyResultsView.as_view()), name='surveyresults'),
    url(r'^(?P<slug>[-_\w]+)/export/$', login_required(SurveyExportView.as_view()), name='exportresults'),
    url(r'^(?P<slug>[-_\w]+)/ballots/$', BallotResultsView.as_view(), name='ballot'),
    url(r'^(?P<slug>[-_\w]+)/qrcode/$', SurveyQRCodeView.as_view(), name='qrcode'),
    url(r'^(?P<slug>[-_\w]+)/dashboard/$', login_required(SurveyDashboardView.as_view()), name='surveydashboard'),
)
