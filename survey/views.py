from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from survey.models import Survey
from django.http import HttpResponseForbidden
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
            # Found in <input name= for this question
            form_input_name = u'q%s' % question.pk
            if form_input_name not in request.POST:
                # The browser doesn't submit blank answers so it won't even be in request.POST
                # Move along to the next question.
                continue
            if question.type in ('TA', 'TB'):
                # Don't have to worry about choices for text inputs
                form_input_value = request.POST.get(form_input_name)
                # Submit the answer
                question.answer_with_text(form_input_value)
            else:
                # Decide which choices were answered for multi-choice inputs
                form_input_values = request.POST.getlist(form_input_name)
                # Clean the form input values from "c##" to ##, ignoring the ones that don't conform
                scrubbed_choice_pks = [int(v[1:]) for v in form_input_values if v.startswith('c') and v[1:].isdigit()]
                # Find all the choice objects being voted on
                chosen_choice_objects = question.choice_set.filter(pk__in=scrubbed_choice_pks)
                # Submit the answers
                question.answer_with_choices(chosen_choice_objects)
        return render_to_response('survey/survey_success.html', context_instance=RequestContext(request))
