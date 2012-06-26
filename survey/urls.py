from django.conf.urls import patterns, url

from survey.views import IndexView, SurveyView

# pylint: disable-msg=C0103,E1120
urlpatterns = patterns(
    'survey.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<slug>[-\w]+)$', SurveyView.as_view(), name='survey'),
)
