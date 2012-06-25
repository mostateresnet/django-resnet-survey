from django.conf.urls import patterns, url

from survey.views import *

# pylint: disable-msg=C0103
urlpatterns = patterns('survey.views',
                       url(r'^$', IndexView.as_view(), name='index'),
                       )
