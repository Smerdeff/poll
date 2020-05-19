import datetime

from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from questionnaire import serializers
from questionnaire.models import *
from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.inspectors import CoreAPICompatInspector, FieldInspector, NotHandled, SwaggerAutoSchema
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework.decorators import action


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
            for param in result:
                if not param.get('description', ''):
                    param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

            return result

        return NotHandled


class NoSchemaTitleInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        # remove the `title` attribute of all Schema objects
        if isinstance(result, openapi.Schema.OR_REF):
            # traverse any references and alter the Schema object in place
            schema = openapi.resolve_ref(result, self.components)
            schema.pop('title', None)

            # no ``return schema`` here, because it would mean we always generate
            # an inline `object` instead of a definition reference

        # return back the same object that we got - i.e. a reference if we got a reference
        return result


class NoTitleAutoSchema(SwaggerAutoSchema):
    field_inspectors = [NoSchemaTitleInspector] + swagger_settings.DEFAULT_FIELD_INSPECTORS


class NoPagingAutoSchema(NoTitleAutoSchema):
    def should_page(self):
        return False


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Получить список анкет",
    filter_inspectors=[DjangoFilterDescriptionInspector], ))
class QuestionnaireViewSet(viewsets.ModelViewSet):
    """
    create:
    Создать анкету

    retrieve:
    Получить анкету с вопросами и вариантами

    update:
    Изменить анкету

    partial_update:
    Изменить анкету

    destroy:
    Удалить анкету
    """
    queryset = Questionnaire.objects.all()
    serializer_class = serializers.QuestionnaireSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('name',)
    ordering_fields = ('date_begin', 'date_end')
    ordering = ('date_begin',)

    swagger_schema = NoTitleAutoSchema

    @swagger_auto_schema(auto_schema=NoPagingAutoSchema, operation_description="Получить список активных анкет",
                         filter_inspectors=[DjangoFilterDescriptionInspector])
    @action(detail=False, methods=['get'])
    def active(self, request):
        date = datetime.datetime.now()
        questionnaires = self.get_queryset().filter(date_end__gte=date).all()
        serializer = self.serializer_class(questionnaires, many=True)
        return Response(serializer.data)

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, noexpand=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'active'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="Получить список вопросов",
                                                             filter_inspectors=[DjangoFilterDescriptionInspector], ))
class QuestionViewSet(viewsets.ModelViewSet):
    """
        create:
        Создать вопрос

        retrieve:
        Получить вопрос с вариантами

        update:
        Изменить вопрос

        partial_update:
        Изменить вопрос

        destroy:
        Удалить вопрос
    """
    queryset = Question.objects.all()
    serializer_class = serializers.QuestionSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('name', 'questionnaire')
    # ordering_fields = ('date_begin', 'date_end')
    # ordering = ('date_begin',)

    swagger_schema = NoTitleAutoSchema

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, noexpand=True)
        return Response(serializer.data)

    @swagger_auto_schema()
    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'active'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="Получить список вариантов",
                                                             filter_inspectors=[DjangoFilterDescriptionInspector], ))
class OptionViewSet(viewsets.ModelViewSet):
    """
        create:
        Создать вариант

        retrieve:
        Получить вариант

        update:
        Изменить вариант

        partial_update:
        Изменить вариант

        destroy:
        Удалить вариант
    """
    queryset = Option.objects.all()
    serializer_class = serializers.OptionSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('question',)
    # ordering_fields = ('date_begin', 'date_end')
    # ordering = ('date_begin',)

    swagger_schema = NoTitleAutoSchema

    @swagger_auto_schema()
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="Список пройденных анкет",
                                                             filter_inspectors=[DjangoFilterDescriptionInspector], ))
class AnswerViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    # mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    """
        create:
        Создать пройденную анкету со всем вопросами и вариантами

        retrieve:
        Получить пройденную анкету

        destroy:
        Удалить пройденную анкету
    """

    queryset = AnswerQuestionnaire.objects.all()
    serializer_class = serializers.AnswerQuestionnaireSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('questionnaire', 'user')
    ordering_fields = ('created_at')
    ordering = ('created_at',)

    swagger_schema = NoTitleAutoSchema

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:  # Не админ видит только свои пройденные анкеты
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, noexpand=True)
        return Response(serializer.data)

    @swagger_auto_schema()
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


@method_decorator(name='list',
                  decorator=swagger_auto_schema(operation_description="Получить список вопросов в пройденых анкетах",
                                                filter_inspectors=[DjangoFilterDescriptionInspector], ))
class AnswerQuestionViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    """
        retrieve:
        Получить вопрос

        partial_update:
        Изменить вопрос

        partial_update:
        Изменить вопрос
    """

    queryset = AnswerQuestion.objects.all()
    serializer_class = serializers.AnswerQuestionSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('answer_questionnaire',)
    # ordering_fields = ('created_at')
    # ordering = ('created_at',)

    swagger_schema = NoTitleAutoSchema

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:  # Не админ видит только свои данные
            queryset = queryset.filter(answer_questionnaire__user=self.request.user)
        return queryset

    def retrieve(self, request, pk):
        answer_question = self.get_queryset().get(pk=pk)
        if answer_question.question_type == 0:
            serializer = serializers.AnswerQuestionTextSerializer(answer_question, many=False)
        else:
            serializer = serializers.AnswerQuestionOptionSerializer(answer_question, many=False)
        # serializer = self.serializer_class(answer_question, many=False)
        return Response(serializer.data)

    def update(self, request, pk, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        print(request.data, pk)
        if self.get_queryset().get(pk=pk).question_type == 0:
            serializer = serializers.AnswerQuestionTextSerializer(instance, data=request.data, partial=partial)
        else:
            serializer = serializers.AnswerQuestionOptionSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @swagger_auto_schema()
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="Список вариантов в ответе",
                                                             filter_inspectors=[DjangoFilterDescriptionInspector], ))
class AnswerOptionViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          # mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
        create:
        Добавить вариант в ответ

        retrieve:
        Получить вариант в ответе

        destroy:
        Удалить вариант в ответе
    """
    queryset = AnswerOption.objects.all()
    serializer_class = serializers.AnswerOptionSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('answer_question',)
    # ordering_fields = ('created_at')
    # ordering = ('created_at',)

    swagger_schema = NoTitleAutoSchema

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:  # Не админ видит только свои данные
            queryset = queryset.filter(answer_question__answer_questionnaire__user=self.request.user)
        return queryset

    @swagger_auto_schema()
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
