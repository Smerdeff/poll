# from django.utils.datetime_safe import datetime
import datetime
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from .models import *
from .serializers import *


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def questionnaires_list(request):
    """
    List questionnaire, or create a new questionnaire.
    """
    if request.method == 'GET':
        nextPage = 1
        previousPage = 1

        active = request.GET.get('active', False)

        if active:
            date = datetime.datetime.utcnow()
            questionnaires = Questionnaire.objects.filter(date_begin__lte=date,date_end__gte=date)  # Активные анкеты только
        else:
            questionnaires = Questionnaire.objects.all()

        page = request.GET.get('page', 1)
        paginator = Paginator(questionnaires, 10)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        serializer = QuestionnaireSerializer(data, context={'request': request}, many=True, noexpand=True)
        if data.has_next():
            nextPage = data.next_page_number()
        if data.has_previous():
            previousPage = data.previous_page_number()

        return Response({'data': serializer.data , 'count': paginator.count, 'numpages' : paginator.num_pages, 'nextlink': 'page=' + str(nextPage), 'prevlink': 'page=' + str(previousPage)})

    elif request.method == 'POST':
        serializer = QuestionnaireSerializer(data=request.data, context={'request': request}, noexpand=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def questionnaire_detail(request, questionnaire_pk):
    """
    Retrieve, update or delete a questionnaire by pk.
    """
    try:
        questionnaire = Questionnaire.objects.get(pk=questionnaire_pk)
    except Questionnaire.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuestionnaireSerializer(questionnaire, context={'request': request},  noexpand=True)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = QuestionnaireSerializer(questionnaire, data=request.data, context={'request': request}, noexpand=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        questionnaire.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def questionnaires_expand(request, questionnaire_pk):
    """
    List questions by questionnaire_pk
    """
    try:
        questionnaire = Questionnaire.objects.get(pk=questionnaire_pk)
    except Questionnaire.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuestionnaireSerializer(questionnaire, context={'request': request})
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def questions_list(request):
    """
    List all questions, Create a new question.
    """
    if request.method == 'GET':
        data = Question.objects.all()
        serializer = QuestionSerializer(data, context={'request': request}, many=True, noexpand=True)
        return Response({'data': serializer.data})

    if request.method == 'POST':
        serializer = QuestionSerializer(data=request.data, noexpand=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def question_detail(request, question_pk):
    """
        Retrieve, update or delete a question by pk.
    """
    try:
        question=Question.objects.get(pk=question_pk)
    except Question.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # raise Exception(question)
    if request.method == 'GET':
        serializer = QuestionSerializer(question, context={'request': request}, noexpand=True)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = QuestionSerializer(question, data=request.data, context={'request': request}, noexpand=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def questions_expand(request, question_pk):
    """
    List answer_options by question_pk
    """
    try:
        question = Question.objects.get(pk=question_pk)
    except Question.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

        # raise Exception(question)
    if request.method == 'GET':
        serializer = QuestionSerializer(question, context={'request': request})
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def options_list(request):
    """
    List all options, Create a new options.
    """
    if request.method == 'GET':
        data = Option.objects.all()
        serializer = OptionSerializer(data, context={'request': request}, many=True)
        return Response({'data': serializer.data})

    if request.method == 'POST':
        serializer = OptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def option_detail(request, option_pk):
    """
    Retrieve, update or delete a options_detail by pk.
    """
    try:
        answer_options = Option.objects.get(pk=option_pk)
    except Option.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OptionSerializer(answer_options, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OptionSerializer(answer_options, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        answer_options.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def answers_list(request):
    """
        List answer, or create a new answer.
    """
    if request.method == 'GET':
        data = AnswerQuestionnaire.objects.filter(user=request.user)
        serializer = AnswerQuestionnaireSerializer(data, context={'request': request}, many=True, noexpand=True)
        return Response({'data': serializer.data})

    elif request.method == 'POST':
        serializer = AnswerQuestionnaireSerializer(data=request.data, context = {'request': request}, noexpand=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def answer_detail(request, answer_pk):
    """
    Retrieve or delete a answer by pk.
    """
    try:
        answer = AnswerQuestionnaire.objects.get(pk=answer_pk)
    except AnswerQuestionnaire.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AnswerQuestionnaireSerializer(answer, context={'request': request}, noexpand=True)
        return Response({'data': serializer.data})

    elif request.method == 'DELETE':
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def answer_expand(request, answer_pk):
    """
    GET answer by pk, or post answer_question with option
    For example:
    {
       "question":1,
       "text":"some text",
       "answer_options":[
          {
             "option":1
          },
          {
             "option":4
          }
       ]
    }
    """
    if request.method == 'GET':
        try:
            answer = AnswerQuestionnaire.objects.get(pk=answer_pk)
        except AnswerQuestionnaire.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerQuestionnaireSerializer(answer, context={'request': request})
        return Response({'data': serializer.data})

    elif request.method == 'POST':
            serializer = AnswerPostSerializer(data=request.data, context={'request': request, 'answer_pk':answer_pk})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
