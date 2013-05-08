try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from survey.views import *

# pylint: disable-msg=C0103,E1120
dashboard_patterns = patterns(
    '',
    url(r'^$', login_required(ensure_csrf_cookie(IndexView.as_view())), name='index'),
    url(r'^new/$', login_required(ensure_csrf_cookie(SurveyNewView.as_view())), name='newsurvey'),
    url(r'^presets/$', login_required(ensure_csrf_cookie(PresetSearchView.as_view())), name='preset_search_view'),
    url(r'^archive/$', login_required(ensure_csrf_cookie(SurveyArchiveView.as_view())), name='surveyarchive'),
    url(r'^(?P<slug>[-_\w]+)/$', login_required(ensure_csrf_cookie(SurveyDashboardView.as_view())), name='surveydashboard'),
    url(r'^(?P<slug>[-_\w]+)/edit/$', login_required(ensure_csrf_cookie(SurveyEditView.as_view())), name='surveyedit'),
    url(r'^(?P<slug>[-_\w]+)/details/$', login_required(ensure_csrf_cookie(SurveyDetailsView.as_view())), name='surveydetails'),
    url(r'^(?P<slug>[-_\w]+)/delete/$', login_required(ensure_csrf_cookie(SurveyDeleteView.as_view())), name='surveydelete'),
    url(r'^(?P<slug>[-_\w]+)/clone/$', login_required(ensure_csrf_cookie(SurveyCloneView.as_view())), name='surveyclone'),
    url(r'^(?P<slug>[-_\w]+)/results/$', login_required(ensure_csrf_cookie(SurveyResultsView.as_view())), name='surveyresults'),
    url(r'^(?P<slug>[-_\w]+)/export/$', login_required(ensure_csrf_cookie(SurveyExportView.as_view())), name='exportresults'),
    url(r'^(?P<slug>[-_\w]+)/(?P<choice_id>\d+)/results/$', login_required(ensure_csrf_cookie(SurveyResultsView.as_view())), name='surveyresults'),
    url(r'^(?P<slug>[-_\w]+)/ballot/(?P<ballot_id>\d+)?$', login_required(ensure_csrf_cookie(BallotResultsView.as_view())), name='ballot'),
)

# pylint: disable-msg=C0103,E1120
urlpatterns = patterns(
    'survey.views',
    url(r'^dashboard/', include(dashboard_patterns)),
    url(r'^(?P<slug>[-_\w]+)/$', SurveyView.as_view(), name='survey'),
    url(r'^(?P<slug>[-_\w]+)_qrcode.png$', SurveyQRCodeView.as_view(), name='qrcode'),
)
