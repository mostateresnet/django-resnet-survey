try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.decorators import login_required
from survey.views import *

# pylint: disable-msg=C0103,E1120
dashboard_patterns = patterns(
    '',
    url(r'^$', login_required(IndexView.as_view()), name='index'),
    url(r'^new/$', login_required(SurveyNewView.as_view()), name='newsurvey'),
    url(r'^presets/$', login_required(PresetSearchView.as_view()), name='preset_search_view'),
    url(r'^archive/$', login_required(SurveyArchiveView.as_view()), name='surveyarchive'),
    url(r'^(?P<slug>[-_\w]+)/$', login_required(SurveyDashboardView.as_view()), name='surveydashboard'),
    url(r'^(?P<slug>[-_\w]+)/edit/$', login_required(SurveyEditView.as_view()), name='surveyedit'),
    url(r'^(?P<slug>[-_\w]+)/duration/$', login_required(SurveyDurationView.as_view()), name='surveyduration'),
    url(r'^(?P<slug>[-_\w]+)/publish/$', login_required(SurveyPublishView.as_view()), name='publishsurvey'),
    url(r'^(?P<slug>[-_\w]+)/close/$', login_required(SurveyCloseView.as_view()), name='closesurvey'),
    url(r'^(?P<slug>[-_\w]+)/delete/$', login_required(SurveyDeleteView.as_view()), name='surveydelete'),
    url(r'^(?P<slug>[-_\w]+)/track/$', login_required(SurveyTrackView.as_view()), name='surveytrack'),
    url(r'^(?P<slug>[-_\w]+)/social/$', login_required(SurveySocialView.as_view()), name='surveysocial'),
    url(r'^(?P<slug>[-_\w]+)/clone/$', login_required(SurveyCloneView.as_view()), name='surveyclone'),
    url(r'^(?P<slug>[-_\w]+)/results/$', login_required(SurveyResultsView.as_view()), name='surveyresults'),
    url(r'^(?P<slug>[-_\w]+)/export/$', login_required(SurveyExportView.as_view()), name='exportresults'),
    url(r'^(?P<slug>[-_\w]+)/(?P<choice_id>\d+)/results/$', login_required(SurveyResultsView.as_view()), name='surveyresults'),
    url(r'^(?P<slug>[-_\w]+)/ballot/(?P<ballot_id>\d+)?$', login_required(BallotResultsView.as_view()), name='ballot'),
)

# pylint: disable-msg=C0103,E1120
urlpatterns = patterns(
    'survey.views',
    url(r'^dashboard/', include(dashboard_patterns)),
    url(r'^(?P<slug>[-_\w]+)/$', SurveyView.as_view(), name='survey'),
    url(r'^(?P<slug>[-_\w]+)_qrcode.png$', SurveyQRCodeView.as_view(), name='qrcode'),
)
