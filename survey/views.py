from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from survey.models import Survey


class IndexView(ListView):
    context_object_name = 'surveys'
    template_name = 'survey/index.html'

    def get_queryset(self):
        return Survey.objects.all()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)
