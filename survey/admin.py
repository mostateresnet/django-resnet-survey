from django.contrib import admin
from survey.models import Survey, Question, Choice, Answer

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Answer)