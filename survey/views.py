import datetime
import json
import qrcode
import xlwt

from django.utils.timezone import now
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views.generic import View, TemplateView, ListView
from django.views.generic.detail import DetailView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.db.models import Q, Count
from django.db import transaction, IntegrityError
from django.utils.translation import ugettext as _

from survey.models import Survey, Question, Ballot, Answer, Choice, Preset, PresetChoice
from survey import settings


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


class AccessMixin(object):
    """
    Requires an implementation of the hasAccess() function which
    determines the requirements for access to a specific view otherwise
    raises a 404 if access is denied.

    For example: results should only be allowed on a closed survey.
    """
    def hasAccess(self):
        raise NotImplementedError("You must implement the hasAccess() method on all DetailAccessView's.")

    def dispatch(self, request, *args, **kwargs):
        handler = super(AccessMixin, self).dispatch(request, *args, **kwargs)
        if not self.hasAccess():
            raise Http404
        return handler


class SurveyDashboardView(AccessMixin, DetailView):
    model = Survey
    template_name = 'survey/survey_dashboard.html'

    def hasAccess(self):
        return True

    def get_context_data(self, *args, **kwargs):
        context = super(SurveyDashboardView, self).get_context_data(*args, **kwargs)
        context.update(survey_list_processor())
        context["current_tab"] = self.template_name
        return context


class SurveyView(View):
    def inactive_survey_response(self, request, duplicate=False):
        response = render_to_response('survey/survey_closed.html',
                                      context_instance=RequestContext(request, {'duplicate': duplicate}))
        response.status_code = 403
        return response

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
        # if survey.use_cookies is true
        # and also check to see if the survey is active
        if (not request.COOKIES.get(survey.cookie, None) or not survey.use_cookies) and survey.is_active:
            response = render_to_response(
                'survey/survey_success.html', context_instance=RequestContext(request, {'redirect': not survey.use_cookies, 'survey': survey}))
            # the cookie doesn't exist yet, it will be added to the response here
            # but only if survey.use_cookies is true
            if (survey.use_cookies):
                response.set_cookie(survey.cookie, value='True', max_age=datetime.timedelta(weeks=settings.COOKIE_EXPIRATION).total_seconds())

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
        return self.inactive_survey_response(request, survey.is_active)


class SurveyEditView(SurveyDashboardView):
    model = Survey
    template_name = 'survey/survey_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SurveyEditView, self).get_context_data(*args, **kwargs)
        context['presets'] = Preset.objects.all()
        return context

    def hasAccess(self):
        return self.get_object().is_unpublished

    def post(self, request, slug):
        survey = self.get_object()
        data = json.loads(request.POST.get('r'))
        questions = data.get('questions', [])
        # delete existing questions
        # due to cascading deletes, this will also delete choices
        survey.question_set.all().delete()
        # edit the title if it has changed
        survey.title = data.get('title', '')
        survey.description = data.get('description', '')
        # edit slug if it has changed
        survey.slug = slugify(data.get('slug', ''))
        try:
            survey.save()
        except IntegrityError:
            return HttpResponse(json.dumps({'status': 'failure', 'error': _('That SLUG already exists')}), mimetype='application/json')
        Question.add_questions(questions, survey)
        return HttpResponse(json.dumps({'status': 'success', 'url': reverse('surveydashboard', args=[survey.slug])}), mimetype='application/json')


class SurveyResultsView(SurveyDashboardView):
    template_name = 'survey/results.html'
    model = Survey

    # order_number (question has an order arg)

    def get_context_data(self, *args, **kwargs):
        context = super(SurveyResultsView, self).get_context_data(*args, **kwargs)
        survey = self.object
        if 'choice_id' in self.kwargs:
            d = Answer.objects.filter(choice=self.kwargs['choice_id']).values_list('ballot', flat=True)
            b = Ballot.objects.filter(pk__in=d)
            q = Answer.objects.filter(ballot__in=b).values_list('choice', flat=True)
            # count_choices choices that have answers
            count_choices = Choice.objects.filter(
                pk__in=q).select_related('question').order_by('question__order_number').annotate(num_answers=Count('answer'))
            # zero_choices choices that do not have answers
            zero_choices = Choice.objects.filter(question__in=survey.question_set.all()) \
                .exclude(Q(question__type='TA') | Q(question__type='TB') | Q(pk__in=count_choices)) \
                .select_related('question')

            combined_choices = []

            for item in zero_choices:
                item.num_answers = 0
                combined_choices.append(item)

            combined_choices.extend(count_choices)
            combined_choices = sorted(combined_choices, key=lambda ch: (ch.question.order_number, ch.pk))

            choices = combined_choices
        else:
            choices = Choice.objects.filter(question__in=survey.question_set.all()).order_by('question').annotate(num_answers=Count('answer'))

        query = {'choices': choices, 'choice_id': int(self.kwargs.get('choice_id', -1))}
        context.update(query)
        return context


class BallotResultsView(SurveyDashboardView):
    template_name = 'survey/survey_ballots.html'

    def get_context_data(self, *args, **kwargs):
        context = super(BallotResultsView, self).get_context_data(*args, **kwargs)
        ballot_id = self.kwargs['ballot_id']
        if ballot_id is None:
            try:
                ballot = self.object.ballot_set.all()[0]
            except IndexError:
                raise Http404
        else:
            ballot = get_object_or_404(Ballot, pk=self.kwargs['ballot_id'], survey=self.object)
        try:
            next_ballot = Ballot.objects.filter(pk__gt=ballot.pk, survey=self.object).order_by('pk')[0]
        except IndexError:
            next_ballot = None
        try:
            previous_ballot = Ballot.objects.filter(pk__lt=ballot.pk, survey=self.object).order_by('-pk')[0]
        except IndexError:
            previous_ballot = None
        context.update({"ballot": ballot, "next_ballot": next_ballot, "previous_ballot": previous_ballot})
        return context


class SurveyNewView(TemplateView):
    template_name = 'survey/survey_form.html'

    def post(self, request):
        data = json.loads(request.POST.get('r'))
        slug = slugify(data.get('slug', ''))
        try:
            survey = Survey.objects.create(slug=slug, title=data.get('title', ''), description=data.get('description', ''), creator=request.user)
        except IntegrityError:
            return HttpResponse(json.dumps({'status': 'failure', 'error': _('That SLUG already exists')}), mimetype='application/json')
        questions = data.get('questions', [])
        Question.add_questions(questions, survey)
        return HttpResponse(json.dumps({'status': 'success', 'url': reverse('surveydashboard', args=[survey.slug])}), mimetype='application/json')

    def get_context_data(self, *args, **kwargs):
        context = super(SurveyNewView, self).get_context_data(*args, **kwargs)
        context['presets'] = Preset.objects.all()
        context.update(survey_list_processor())
        return context


class SurveyDurationView(SurveyDashboardView):
    def get(self, request):
        return Http404()

    def post(self, request, slug):
        errors = []
        if 'set_duration' in request.POST:
            survey = Survey.objects.get(slug=slug)

            if survey.start_date and survey.start_date < now() and self.get_object().has_results:
                errors.append('A surveys publish date cannot be changed if it has already gone live.')
            else:
                survey.set_date('start_date',
                                request.POST.get('start_date', ''),
                                request.POST.get('start_time', '')
                                )
                if 'end_date' in request.POST:
                    survey.set_date('end_date',
                                    request.POST.get('end_date', ''),
                                    request.POST.get('end_time', '')
                                    )
        if errors:
            return HttpResponse(json.dumps({
                'status': 'error',
                'errors': errors
            }), mimetype='application/json')
        return HttpResponse(json.dumps({
            'status': 'success',
            'success': ''
        }), mimetype='application/json')


class SurveyPublishView(View):
    def get(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        if request.user.is_staff:
            survey.publish()
        return HttpResponseRedirect(reverse('index'))


class SurveyTrackView(View):
    def get(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        if request.user.is_staff:
            survey.track(not survey.use_cookies)
        return HttpResponseRedirect(reverse('surveydashboard', args=[slug]))


class SurveyCloseView(View):
    def get(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        if request.user.is_staff:
            survey.close()
        return HttpResponseRedirect(reverse('index'))


class SurveyDeleteView(View):
    def post(self, request, slug):
        if request.user.is_staff:
            Survey.objects.filter(slug=slug).delete()
        return HttpResponseRedirect(reverse('index'))


class SurveyCloneView(View):
    # Ajax View
    def post(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        if request.user.is_staff:
            if request.method == 'POST' and 'title' in request.POST:
                title = request.POST.get('title', '')
                try:
                    new_survey = Survey.objects.create(title=title, slug=slugify(title))
                    # survey successfully created
                    survey.clone(new_survey)
                except IntegrityError:
                    return HttpResponse(json.dumps({
                        'status': 'IntegrityError',
                        'error': _('A survey with that title already exists.')
                    }), mimetype='application/json')
                return HttpResponse(json.dumps({
                    'status': 'success',
                    'url': reverse('surveydashboard', args=(new_survey.slug,))
                }), mimetype='application/json')
        return HttpResponse(json.dumps({'status': 'Auth Error', 'error': _('You are not authorized to do that.')}), mimetype='application/json')


class SurveyQRCodeView(View):
    def get(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        img = qrcode.make(settings.HOST_URL + survey.get_absolute_url())
        response = HttpResponse(mimetype='image/png')
        response['Content-Disposition'] = 'attachment; filename=%s.png' % survey.slug
        img.save(response, 'PNG')
        return response


class SurveyExportView(SurveyDashboardView):

    def hasAccess(self):
        return self.get_object().has_results

    def generateExcelSummary(self, survey):
        wb = xlwt.Workbook()
        ws = wb.add_sheet(_('Survey Results'))
        ws_text = wb.add_sheet(_('Text Results'))

        question_font = xlwt.Font()
        question_font.bold = True
        question_style = xlwt.XFStyle()
        question_style.font = question_font
        ws.col(0).width = 256 * 50
        ws_text.col(0).width = 256 * 75

        ws.write(0, 0, _("Question"), question_style)
        ws.write(0, 1, _("Tally"), question_style)

        ws_text.write(0, 0, _("Question"), question_style)

        text_question_style = xlwt.easyxf("align: wrap on")

        counter = 2
        counter_text = 0
        for question in survey.question_set.all():
            ws.write(counter, 0, str(question), question_style)
            if question.type == 'TB' or question.type == 'TA':
                counter_text += 2
                ws_text.write(counter_text, 0, str(question), question_style)
                counter += 1
                ws.write(counter, 0, xlwt.Formula("HYPERLINK(\"#TextResults!A" + str(counter_text + 1) + "\", \"Click to see text results\")"))
                for choice in question.choice_set.all():
                    for answer in choice.answer_set.all():
                        counter_text += 1
                        ws_text.row(counter_text).height = 256 * 3
                        ws_text.write(counter_text, 0, str(answer), text_question_style)
            elif question.type == 'RA' or question.type == 'CH' or question.type == 'DD':
                for choice in question.choice_set.all():
                    counter += 1
                    ws.write(counter, 0, str(choice))
                    ws.write(counter, 1, choice.answer_set.count())
            counter += 2
        return wb

    def generateExcelFull(self, survey):
        wb = xlwt.Workbook()
        ws = wb.add_sheet(_('Survey Results'))

        question_font = xlwt.Font()
        question_font.bold = True
        question_style = xlwt.XFStyle()
        question_style.font = question_font

        col_counter = 1
        for question in survey.question_set.all():
            ws.col(col_counter).width = 256 * 30
            ws.write(0, col_counter, str(question), question_style)
            col_counter = col_counter + 1

        row_counter = 1
        for ballot in survey.ballot_set.all():
            col_counter = 1
            ws.write(row_counter, 0, str(ballot.pk))
            for answer in ballot.answer_list():

                ws.write(row_counter, col_counter, ','.join(answer))
                col_counter = col_counter + 1
            row_counter = row_counter + 1
        return wb

    def get(self, request, slug):
        survey = self.get_object()
        if not request.user.is_staff:
            return HttpResponseForbidden()

        if 'rtype' in request.GET:
            if request.GET['rtype'] == 'Summary':
                wb = self.generateExcelSummary(survey)
            elif request.GET['rtype'] == 'Full':
                wb = self.generateExcelFull(survey)

            report_title = "Test Report"
            date = datetime.datetime.now().strftime("%m-%d-%Y")
            response = HttpResponse(mimetype='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Report_%s_%s.xls' % ('_'.join(report_title.split()), date)

            wb.save(response)

            return response
        else:
            return HttpResponse(json.dumps({'status': 'failure', 'error': _('Report type not selected!')}), mimetype='application/json')


class SurveyReorderView(SurveyDashboardView):
    template_name = 'survey/reorder.html'

    def hasAccess(self):
        return self.get_object().is_unpublished

    def post(self, request, slug):
        # get POST data
        orderDict = request.POST
        # update questions with new order_number
        with transaction.commit_on_success():
            for pk, order in orderDict.iteritems():
                pk = pk[3:]
                Question.objects.filter(pk=pk).update(order_number=order[0])
        # return success
        return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')


class PresetSearchView(DetailView):
    def get(self, request):
        all_choices = PresetChoice.objects.filter(preset__title__iexact=self.request.GET.get('title', ''))
        return HttpResponse(json.dumps({'status': 'success', 'values': list(all_choices.values_list('option', flat=True))}), mimetype='application/json')
