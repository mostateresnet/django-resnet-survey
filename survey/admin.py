from django.contrib import admin
from survey.models import Survey, Question, Choice, Answer, Ballot, Preset, PresetChoice


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


class PresetChoiceInline(admin.TabularInline):
    model = PresetChoice
    extra = 1


class SurveyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [
        QuestionInline,
    ]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        ChoiceInline,
    ]


class BallotAdmin(admin.ModelAdmin):
    list_display = [
        'ip',
        'datetime',
    ]


class PresetAdmin(admin.ModelAdmin):
    inlines = [
        PresetChoiceInline,
    ]

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Ballot, BallotAdmin)
admin.site.register(Preset, PresetAdmin)
admin.site.register(Choice)
admin.site.register(Answer)
