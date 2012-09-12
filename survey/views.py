from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic.list import ListView
from survey.models import Survey, Question, Choice, Ballot
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View, TemplateView
from django.views.generic.detail import DetailView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json


class IndexView(TemplateView):
    template_name = 'survey/index.html'
    def get_context_data(self, **kwargs):
        return {
            'published_surveys': Survey.objects.filter(Q(end_date__isnull=True) | Q(end_date__gte=now()), start_date__lte=now()),
            'unpublished_surveys': Survey.objects.filter(start_date__isnull=True),
        }

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)


class SurveyView(View):
    def inactive_survey_response(self, request):
        return HttpResponseForbidden(render_to_response('survey/survey_closed.html', context_instance=RequestContext(request)))

    def get(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        if not survey.is_active and not request.user.is_staff:
            return self.inactive_survey_response(request)
        return render_to_response('survey/survey.html', {'survey': Survey.objects.get(slug=slug)}, context_instance=RequestContext(request))

    def post(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        if not survey.is_active:
            return self.inactive_survey_response(request)
        ballot = Ballot.objects.create(ip=request.META['REMOTE_ADDR'], survey=survey)
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
                question.answer_with_text(form_input_value, ballot)
            else:
                # Decide which choices were answered for multi-choice inputs
                form_input_values = request.POST.getlist(form_input_name)
                # Clean the form input values from "c##" to ##, ignoring the ones that don't conform
                scrubbed_choice_pks = [int(v[1:]) for v in form_input_values if v.startswith('c') and v[1:].isdigit()]
                # Find all the choice objects being voted on
                chosen_choice_objects = question.choice_set.filter(pk__in=scrubbed_choice_pks)
                # Submit the answers
                question.answer_with_choices(chosen_choice_objects, ballot)
        return render_to_response('survey/survey_success.html', context_instance=RequestContext(request))


class SurveyEditView(DetailView):
    model = Survey
    template_name = 'survey/survey_edit.html'

    def post(self, request, slug):
        survey = self.get_object()
#        Question.objects.filter( pk__in=request.POST.get('data') )
        data = json.loads(request.POST.get('r'))
        questions = data.get('questions', [])
        # delete existing questions
        # due to cascading deletes, this will also delete choices
        survey.question_set.all().delete()
        # edit the title if it has changed
        title = data.get('title', '')
        if survey.title != title:
            survey.delete()
            survey = Survey.objects.create(slug=slugify(title), title=title)
        Question.add_questions(questions, survey)
        return HttpResponse('created')
        
        
        

class SurveyResultsView(DetailView):
    template_name = 'survey/results.html'
    model = Survey


class BallotResultsView(DetailView):
    def get(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        ballot_list = survey.ballot_set.all()
        paginator = Paginator(ballot_list, 1)

        page = request.GET.get('page')
        try:
            ballots = paginator.page(page)
        except PageNotAnInteger:
            ballots = paginator.page(1)
        except EmptyPage:
            ballots = paginator.page(paginator.num_pages)
        return render_to_response('survey/ballots.html', {"ballots": ballots, "survey": survey})


class SurveyNewView(View):
    def get(self, request):
        return render_to_response('survey/survey_new.html', context_instance=RequestContext(request))

    def post(self, request):
        data = json.loads(request.POST.get('r'))
        slug = slugify(data.get('title', ''))
        survey = Survey.objects.create(slug=slug, title=data.get('title', ''))
        questions = data.get('questions', [])
        survey.save()
        Question.add_questions(questions, survey)
        return HttpResponse('created')

class SurveyPublishView(View):
    def get(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        if request.user.is_staff:
            survey.publish()
        return HttpResponseRedirect(reverse('index'))

class SurveyQRCodeView(View):
    def get(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        return survey.get_qr_code()