import datetime

from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

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


#
# class QuestionnairePagination(LimitOffsetPagination):
#     default_limit = 5
#     max_limit = 25
#
#
# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 100
#     page_size_query_param = 'page_size'
#     max_page_size = 1000



@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Get questionnaires list",
    filter_inspectors=[DjangoFilterDescriptionInspector], ))
class QuestionnaireViewSet(viewsets.ModelViewSet):
    """
    QuestionnaireViewSet
    """
    queryset = Questionnaire.objects.all()
    serializer_class = serializers.QuestionnaireSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('name',)
    ordering_fields = ('date_begin', 'date_end')
    ordering = ('date_begin',)

    swagger_schema = NoTitleAutoSchema

    @swagger_auto_schema(auto_schema=NoPagingAutoSchema, filter_inspectors=[DjangoFilterDescriptionInspector])
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

    # def list(self, request):
    #     questionnaires = self.get_queryset()
    #     serializer = self.serializer_class(questionnaires, many=True, noexpand=True)
    #     return Response(serializer.data)

    #
    # @swagger_auto_schema(method='get', operation_description="image GET description override")
    # @swagger_auto_schema(method='post', request_body=serializers.ImageUploadSerializer)
    # @swagger_auto_schema(method='delete', manual_parameters=[openapi.Parameter(
    #     name='delete_form_param', in_=openapi.IN_FORM,
    #     type=openapi.TYPE_INTEGER,
    #     description="this should not crash (form parameter on DELETE method)"
    # )])
    # @action(detail=True, methods=['get', 'post', 'delete'], parser_classes=(MultiPartParser, FileUploadParser))
    # def image(self, request, slug=None):
    #     """
    #     image method docstring
    #     """
    #     pass

    # def retrieve(self, request, pk=None):
    #     pass

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'active'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


        # @swagger_auto_schema(request_body=no_body, operation_id='no_body_test')
        # def update(self, request, *args, **kwargs):
        #     """update method docstring"""
        #     return super(QuestionnaireViewSet, self).update(request, *args, **kwargs)

        # @swagger_auto_schema(operation_description="partial_update description override", responses={404: 'slug not found'},
        #                      operation_summary='partial_update summary', deprecated=True)
        # def partial_update(self, request, *args, **kwargs):
        #     """partial_update method docstring"""
        #     return super(QuestionnaireViewSet, self).partial_update(request, *args, **kwargs)
        #
        # def update(self, request, *args, **kwargs):
        #     """update method docstring"""
        #     return super(QuestionnaireViewSet, self).partial_update(request, *args, **kwargs)
        #
        #
        # def destroy(self, request, *args, **kwargs):
        #     """destroy method docstring"""
        #     return super(QuestionnaireViewSet, self).destroy(request, *args, **kwargs)
        #
        #


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="Get questions list",
                                                             filter_inspectors=[DjangoFilterDescriptionInspector], ))
class QuestionViewSet(viewsets.ModelViewSet):
    """
    Questions ViewSet
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

    # def list(self, request):
    #     questions = self.get_queryset()
    #     serializer = self.serializer_class(questions, many=True, noexpand=True)
    #     return Response(serializer.data)

    @swagger_auto_schema()
    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'active'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="Get options list",
                                                             filter_inspectors=[DjangoFilterDescriptionInspector], ))
class OptionViewSet(viewsets.ModelViewSet):
    """
    Options ViewSet
    """
    queryset = Option.objects.all()
    serializer_class = serializers.OptionSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('option',)
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


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="Get answer questionnaires list",
                                                             filter_inspectors=[DjangoFilterDescriptionInspector], ))
class AnswerViewSet(viewsets.ModelViewSet):
    """
    Answer ViewSet
    """
    # raise Exception(permission_classes)
    queryset = AnswerQuestionnaire.objects.all()
    serializer_class = serializers.AnswerQuestionnaireSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('questionnaire',)
    ordering_fields = ('created_at')
    ordering = ('created_at',)

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
        if self.action in ('list', 'retrieve', 'create'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="Get answer questions list",
                                                             filter_inspectors=[DjangoFilterDescriptionInspector], ))
class AnswerQuestionViewSet(viewsets.ModelViewSet):
    """
    AnswerQuestion ViewSet
    """
    queryset = AnswerQuestion.objects.all()
    serializer_class = serializers.AnswerQuestionSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('answer_questionnaire',)
    # ordering_fields = ('created_at')
    # ordering = ('created_at',)

    swagger_schema = NoTitleAutoSchema

    @swagger_auto_schema()
    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="Get answer options list",
                                                             filter_inspectors=[DjangoFilterDescriptionInspector], ))
class AnswerOptionViewSet(viewsets.ModelViewSet):
    """
    AnswerOption ViewSet
    """
    queryset = AnswerOption.objects.all()
    serializer_class = serializers.AnswerOptionSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    # filterset_fields = ('answer_questionnaire',)
    # ordering_fields = ('created_at')
    # ordering = ('created_at',)

    swagger_schema = NoTitleAutoSchema

    @swagger_auto_schema()
    def get_permissions(self):
        # if self.action in ('list', 'retrieve', 'create' ):
        #     permission_classes = [IsAuthenticated]
        # else:
        permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
