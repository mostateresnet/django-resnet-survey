from django.contrib import admin
from survey.models import Survey, Question, Choice, Answer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    
class SurveyAdmin(admin.ModelAdmin):
    inlines=[
        QuestionInline,
    ]
    
class QuestionAdmin(admin.ModelAdmin):
    inlines=[
        ChoiceInline,
    ]
    

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Answer)