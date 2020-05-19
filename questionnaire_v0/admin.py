from django.contrib import admin
from questionnaire.models import *
# Register your models here.

admin.site.register(Questionnaire)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(AnswerQuestionnaire)
admin.site.register(AnswerQuestion)
admin.site.register(AnswerOption)

