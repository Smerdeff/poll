from rest_framework import serializers
# from .models import *
from .models import *
from django.db import transaction

class OptionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        noparent = kwargs.pop('noparent', None)

        super(OptionSerializer, self).__init__(*args, **kwargs)

        if noparent:
            self.fields.pop('question')

    def validate(self, data):
        if data['question'].question_type == QT_TEXT:
            raise serializers.ValidationError("Question type not for options. Only text.")

        return data

    class Meta:
        model = Option
        fields = ('pk', 'option', 'question')


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True, noparent=True, default=[])

    def __init__(self, *args, **kwargs):
        noexpand = kwargs.pop('noexpand', None)
        noparent = kwargs.pop('noparent', None)

        super(QuestionSerializer, self).__init__(*args, **kwargs)

        if noexpand:
            self.fields.pop('options')
        if noparent:
            self.fields.pop('questionnaire')

    class Meta:
        model = Question
        fields = ('pk', 'name', 'question_type', 'questionnaire', 'options')


class QuestionnaireSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True, noparent=True, default=[])

    def __init__(self, *args, **kwargs):
        noexpand = kwargs.pop('noexpand', None)
        super(QuestionnaireSerializer, self).__init__(*args, **kwargs)

        if noexpand:
            self.fields.pop('questions')

    class Meta:
        model = Questionnaire
        fields = ('pk', 'name', 'date_begin', 'date_end', 'description', 'questions')


class AnswerOptionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        noparent = kwargs.pop('noparent', None)
        super(AnswerOptionSerializer, self).__init__(*args, **kwargs)
        if noparent:
            self.fields.pop('answer_question')

    def validate(self, data):
        if data['answer_question'].question_type == QT_TEXT:
            raise serializers.ValidationError("Question type not for Option. Only Text.")

        if not AnswerQuestionnaire.objects.filter(pk=data['answer_question'].answer_questionnaire.pk, user=self.context['request'].user).exists():
            raise serializers.ValidationError("No AnswerQuestionnaire pk {0} for this User".format(data['answer_question'].answer_questionnaire.pk))

        if not Option.objects.filter(question=data['answer_question'].question.pk, pk=data['option'].pk).exists():
            raise serializers.ValidationError("Invalid Option pk {0} for Question pk {1}".format(data['option'].pk,data['answer_question'].question.pk ))

        if data['answer_question'].question_type == QT_CHOICES:
            if AnswerOption.objects.filter(answer_question=data['answer_question'].pk).exists():
                raise serializers.ValidationError("Question type for only 1 options")
        return data

    class Meta:
        model = AnswerOption
        fields = ('pk', 'answer_question', 'option')


# Общий Serializer для AnswerQuestion
class AnswerQuestionSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, noparent=True, read_only=True)

    def __init__(self, *args, **kwargs):
        noexpand = kwargs.pop('noexpand', None)
        noparent = kwargs.pop('noparent', None)

        super(AnswerQuestionSerializer, self).__init__(*args, **kwargs)

        if noexpand:
            self.fields.pop('answer_options')
        if noparent:
            self.fields.pop('answer_questionnaire')

    class Meta:
        model = AnswerQuestion
        fields = ('pk', 'answer_questionnaire', 'question', 'text', 'question_type', 'answer_options')
        read_only_fields = ('answer_questionnaire', 'question', 'question_type')


# Serializer для AnswerQuestion для текста
class AnswerQuestionTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerQuestion
        fields = ('pk', 'answer_questionnaire', 'question', 'text', 'question_type')
        read_only_fields = ('answer_questionnaire', 'question', 'question_type')


# Serializer для AnswerQuestion для выбора
class AnswerQuestionOptionSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, noparent=True, read_only=True)

    class Meta:
        model = AnswerQuestion
        fields = ('pk', 'answer_questionnaire', 'question', 'question_type', 'answer_options',)
        read_only_fields = ('answer_questionnaire', 'question', 'question_type', 'text')



class AnswerQuestionnaireSerializer(serializers.ModelSerializer):
    answer_questions = AnswerQuestionSerializer(many=True, noparent=True, read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def __init__(self, *args, **kwargs):
        noexpand = kwargs.pop('noexpand', None)
        super(AnswerQuestionnaireSerializer, self).__init__(*args, **kwargs)
        if noexpand:
            self.fields.pop('answer_questions')

    def create(self, validated_data):
        with transaction.atomic():
            answer_questionnaire = super(AnswerQuestionnaireSerializer, self).create(validated_data)
            questions = Question.objects.filter(questionnaire=answer_questionnaire.questionnaire)
            AnswerQuestion.objects.bulk_create([AnswerQuestion(answer_questionnaire=answer_questionnaire, question=question,
                                                               question_type=question.question_type) for question in
                                                questions])
            AnswerOption.objects.bulk_create([AnswerOption(answer_questionnaire=answer_questionnaire, question=question,
                                                           question_type=question.question_type) for question in
                                              questions])
        return answer_questionnaire

    class Meta:
        model = AnswerQuestionnaire
        fields = ('pk', 'questionnaire', 'created_at', 'user', 'answer_questions')


# Не используется в текущей редакции
class AnswerPostSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, noparent=True, default=[])

    def create(self, validated_data):
        try:
            aq = AnswerQuestionnaire.objects.get(pk=self.context['answer_pk'], user=self.context['request'].user)
        except:
            raise serializers.ValidationError(
                "No AnswerQuestionnaire pk = {0} for this user".format(self.context['answer_pk']))

        answer_options_data = validated_data.pop('answer_options')

        # TODO переделать удаление на обновления.
        try:
            answer_question = AnswerQuestion.objects.get(answer_questionnaire=aq.pk,
                                                         question=validated_data['question'])
            answer_question.delete()
        except:
            pass

        answer_question = AnswerQuestion.objects.create(answer_questionnaire=aq, **validated_data)
        option = Option.objects.filter(question=validated_data['question'])

        # TODO Может надо кидать экспешн, если дают не корректный option. Сейчас сохраняют только корректный
        for answer_option_data in answer_options_data:
            for e in option:
                if e == answer_option_data['option']:
                    AnswerOption.objects.create(answer_question=answer_question, **answer_option_data)

        return answer_question

    def validate(self, data):
        if data['question'].question_type != QT_TEXT and data.get('text'):
            raise serializers.ValidationError("Question type not for text. Only Option.")

        if data['question'].question_type == QT_TEXT and len(data.get('answer_options')) > 0:
            raise serializers.ValidationError("Question type not for options. Only text.")

        if data['question'].question_type == 1 and len(data.get('answer_options')) > 1:
            raise serializers.ValidationError("Question type for only 1 options.")

        return data

    class Meta:
        model = AnswerQuestion
        fields = ('pk', 'question', 'text', 'answer_options')
