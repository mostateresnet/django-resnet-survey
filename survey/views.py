from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from survey.models import Survey, Choice, Answer
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext


class IndexView(ListView):
    context_object_name = 'surveys'
    template_name = 'survey/index.html'

    def get_queryset(self):
        return Survey.objects.all()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)


class SurveyView(View):
    def dispatch(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        if survey.is_active:
            # Survey is active; carry on as normal
            return super(SurveyView, self).dispatch(request, slug)
        else:
            # Survey is closed; stop here and show an error message.
            return HttpResponseForbidden(render_to_response('survey/survey_closed.html', context_instance=RequestContext(request)))

    def get(self, request, slug):
        return render_to_response('survey/survey.html', {'survey': Survey.objects.get(slug=slug)}, context_instance=RequestContext(request))

    def post(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        for question in survey.question_set.all():
            if unicode(u'q' + unicode(question.pk)) in request.POST:
                for choice_pk in request.POST.getlist(u'q' + unicode(question.pk)):
                    try:
                        choice = Choice.objects.get(pk=int(choice_pk[1:]))
                    except ValueError:
                        choice = question.choice_set.all()[0]
                    Answer.objects.create(choice=choice, text=choice_pk)
        return HttpResponse('Thank you, your survey has been submitted.')
