from django.utils.timezone import now
from survey.models import Survey, Question, Ballot
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View, TemplateView
from django.views.generic.detail import DetailView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import timedelta
from survey import settings
import json
import qrcode
import xlwt
import datetime


def survey_list_processor(request=None):
    return {
    'published_surveys': Survey.objects.filter(Q(end_date__isnull=True) | Q(end_date__gte=now()), start_date__lte=now()),
    'unpublished_surveys': Survey.objects.filter(Q(start_date__isnull=True) | Q(start_date__gt=now())),
    'closed_surveys': Survey.objects.filter(start_date__isnull=False, end_date__lte=now()).order_by('end_date')[:10]
    }


class IndexView(TemplateView):
    template_name = 'survey/index.html'

    def get_context_data(self, *args, **kwargs):
        return survey_list_processor()


class SurveyDashboardView(DetailView):
    model = Survey
    template_name = 'survey/survey_dashboard.html'

    def post(self, request, slug):
        survey = self.get_object()
        if 'future_publish_date' in request.POST:
            survey.set_future_date('start_date', request.POST.get('future_publish_date', ''))
            self.template_name = 'survey/ajax/future_publish.html'
        elif 'future_close_date' in request.POST:
            survey.set_future_date('end_date', request.POST.get('future_close_date', ''))
            self.template_name = 'survey/ajax/future_close.html'
        return self.get(request, slug)

    def get_context_data(self, *args, **kwargs):
        context = super(SurveyDashboardView, self).get_context_data(*args, **kwargs)
        context.update(survey_list_processor())
        return context


class SurveyView(View):
    def inactive_survey_response(self, request, duplicate=False):
        return HttpResponseForbidden(
            render_to_response('survey/survey_closed.html',
                               context_instance=RequestContext(request, {'duplicate': duplicate})
                               )
        )

    def get(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        # if the survey is not active
        # and the user is not staff
        if not survey.is_active and not request.user.is_staff:
            return self.inactive_survey_response(request, bool(request.COOKIES.get(survey.cookie, None)))
        return render_to_response('survey/survey.html', {'survey': Survey.objects.get(slug=slug)}, context_instance=RequestContext(request))

    def post(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        # prevent ballot stuffing by checking for the cookie
        # and also check to see if the survey is active
        if not request.COOKIES.get(survey.cookie, None) and survey.is_active:
            response = render_to_response('survey/survey_success.html', context_instance=RequestContext(request))
            # the cookie doesn't exist yet, it will be added to the response here
            response.set_cookie(survey.cookie, value='True', max_age=timedelta(weeks=settings.COOKIE_EXPIRATION).total_seconds())
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
            return response
        # if either are false return a forbidden response
        return self.inactive_survey_response(request)


class SurveyEditView(SurveyDashboardView):
    model = Survey
    template_name = 'survey/survey_edit.html'

    def post(self, request, slug):
        survey = self.get_object()
        data = json.loads(request.POST.get('r'))
        questions = data.get('questions', [])
        # delete existing questions
        # due to cascading deletes, this will also delete choices
        survey.question_set.all().delete()
        # edit the title if it has changed
        survey.title = data.get('title')
        survey.save()
        Question.add_questions(questions, survey)
        return HttpResponse(json.dumps({'status': 'success', 'url': survey.get_absolute_url()}), mimetype='application/json')


class SurveyResultsView(SurveyDashboardView):
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


class SurveyNewView(TemplateView):
    template_name = 'survey/survey_new.html'

    def post(self, request):
        data = json.loads(request.POST.get('r'))
        slug = slugify(data.get('title', ''))
        survey = Survey.objects.create(slug=slug, title=data.get('title', ''))
        questions = data.get('questions', [])
        survey.save()
        Question.add_questions(questions, survey)
        return HttpResponse(json.dumps({'status': 'success', 'url': survey.get_absolute_url()}), mimetype='application/json')

    def get_context_data(self, *args, **kwargs):
        context = super(SurveyNewView, self).get_context_data(*args, **kwargs)
        context.update(survey_list_processor())
        return context


class SurveyPublishView(View):
    def get(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        if request.user.is_staff:
            survey.publish()
        return HttpResponseRedirect(reverse('index'))


class SurveyCloseView(View):
    def get(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        if request.user.is_staff:
            survey.close()
        return HttpResponseRedirect(reverse('index'))


class SurveyQRCodeView(View):
    def get(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        img = qrcode.make(settings.HOST_URL + survey.get_absolute_url())
        response = HttpResponse(mimetype='image/png')
        response['Content-Disposition'] = 'attachment; filename=%s.png' % survey.slug
        img.save(response, 'PNG')
        return response

class SurveyExportView(View):
    def get(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        if not request.user.is_staff:
            return HttpResponseForbidden()

        wb = xlwt.Workbook()
        ws = wb.add_sheet('A Test Sheet')

        question_font = xlwt.Font()
        question_font.bold = True
        question_style = xlwt.XFStyle()
        question_style.font = question_font
        ws.col(0).width = 256*50

        ws.write(0, 0, "Question", question_style)
        ws.write(0, 1, "Tally", question_style)

        counter = 2
        for question in survey.question_set.all():
            ws.write(counter, 0, str(question), question_style)
            if question.type == 'TB' or question.type == 'TA':
                for choice in question.choice_set.all():
                    for answer in choice.answer_set.all():
                        counter += 1
                        ws.write(counter, 0, str(answer))
            elif question.type == 'RA' or question.type == 'CH' or question.type == 'DD':
                for choice in question.choice_set.all():
                    counter += 1
                    ws.write(counter, 0, str(choice))
                    ws.write(counter, 1, choice.answer_set.count())
            counter += 2

        report_title="Test Report"
        date = datetime.datetime.now().strftime("%m-%d-%Y")
        response = HttpResponse(mimetype='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=Report_%s_%s.xls' % ('_'.join(report_title.split()), date)

        wb.save(response)

        return response
