from django.conf.urls import patterns, url

from survey.views import IndexView, SurveyView, SurveyResultsView, SurveyMobileView

# pylint: disable-msg=C0103,E1120
urlpatterns = patterns(
    'survey.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<slug>[-_\w]+)/$', SurveyView.as_view(), name='survey'),
    url(r'^(?P<slug>[-_\w]+)/results/$', SurveyResultsView.as_view(), name='surveyresults'),
    url(r'^(?P<slug>[-_\w]+)/mobile/$', SurveyMobileView.as_view(), name='surveymobile'),
)
