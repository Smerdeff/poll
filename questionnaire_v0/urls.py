from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from .views import *
from .models import *

# urlpatterns = router.urls

urlpatterns = [
    url(r'^questionnaires/$', questionnaires_list),
    url(r'^questionnaires/(?P<questionnaire_pk>[0-9]+)/$', questionnaire_detail),
    url(r'^questionnaires/(?P<questionnaire_pk>[0-9]+)/questions/$', questionnaires_expand),

    url(r'^questions/$', questions_list),
    url(r'^questions/(?P<question_pk>[0-9]+)/$', question_detail),
    url(r'^questions/(?P<question_pk>[0-9]+)/options/$', questions_expand),

    url(r'^options/$', options_list),
    url(r'^options/(?P<option_pk>[0-9]+)/$', option_detail),

    url(r'^answers/$', answers_list),
    url(r'^answers/(?P<answer_pk>[0-9]+)/$', answer_detail),
    url(r'^answers/(?P<answer_pk>[0-9]+)/answer_question/$', answer_expand),

    # url(r'^answer_option/$', answer_option_post),
    # url(r'^answer_option/(?P<answers_detail_pk>[0-9]+)/$', answer_option_detail),
    #
]