from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from questionnaire import views

router = SimpleRouter()
router.register('questionnaires', views.QuestionnaireViewSet)
router.register('questions', views.QuestionViewSet)
router.register('options', views.OptionViewSet)
router.register('answers', views.AnswerViewSet)
router.register('answer_questions', views.AnswerQuestionViewSet)
router.register('answer_options', views.AnswerOptionViewSet)




urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(router.urls)),
]


# router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='user')
# urlpatterns = router.urls