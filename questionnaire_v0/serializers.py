from django.utils.timezone import now
from rest_framework import serializers
# from .models import *
from questionnaire.models import Option, Question, Questionnaire, AnswerQuestion, AnswerOption, AnswerQuestionnaire


class OptionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        noparent = kwargs.pop('noparent', None)

        super(OptionSerializer, self).__init__(*args, **kwargs)

        if noparent:
            self.fields.pop('question')

    def validate(self, data):
        if data['question'].question_type == 0:
            raise serializers.ValidationError("Question type not for options. Only text.")

        return data
    class Meta:
        model = Option
        fields = ('pk','option', 'question')

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True, noparent=True)

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
        fields = ('pk','name', 'question_type', 'questionnaire' , 'options')

class QuestionnaireSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=False,  noparent=True)

    def __init__(self, *args, **kwargs):
        noexpand = kwargs.pop('noexpand', None)
        super(QuestionnaireSerializer, self).__init__(*args, **kwargs)

        if noexpand:
            self.fields.pop('questions')

    class Meta:
        model = Questionnaire
        fields = ('pk','name', 'date_begin', 'date_end', 'description', 'questions')


class AnswerOptionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        noparent = kwargs.pop('noparent', None)

        super(AnswerOptionSerializer, self).__init__(*args, **kwargs)

        if noparent:
            self.fields.pop('answer_question')

    class Meta:
        model = AnswerOption
        fields = ('pk', 'answer_question', 'option')


class AnswerQuestionSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, noparent=True)

    def __init__(self, *args, **kwargs):
        noexpand = kwargs.pop('noexpand', None)
        noparent = kwargs.pop('noparent', None)

        super(AnswerQuestionSerializer, self).__init__(*args, **kwargs)

        if noexpand:
            self.fields.pop('answer_options')
        if noparent:
            self.fields.pop('answer_questionnaire')

    def validate(self, data):
        if data['question'].question_type == 1:
            if AnswerOption.objects.filter(question=data['question']).exists():
                raise serializers.ValidationError("Question type for only 1 options.")
        return data

    class Meta:
        model = AnswerQuestion
        fields = ('pk', 'question', 'text', 'answer_options', 'answer_questionnaire' )
        depth=0

class AnswerQuestionnaireSerializer(serializers.ModelSerializer):
    answer_questions = AnswerQuestionSerializer(many=True, noparent=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def __init__(self, *args, **kwargs):
        noexpand = kwargs.pop('noexpand', None)

        super(AnswerQuestionnaireSerializer, self).__init__(*args, **kwargs)

        if noexpand:
            self.fields.pop('answer_questions')

    class Meta:
        model = AnswerQuestionnaire
        fields = ('pk', 'questionnaire', 'created_at', 'user', 'answer_questions')
        depth=0


class AnswerPostSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, noparent=True, default=[])

    def create(self, validated_data):
        try:
            aq = AnswerQuestionnaire.objects.get(pk=self.context['answer_pk'], user=self.context['request'].user)
        except:
            raise serializers.ValidationError("No AnswerQuestionnaire pk = {0} for this user".format(self.context['answer_pk']))

        answer_options_data = validated_data.pop('answer_options')

        #TODO переделать удаление на обновления.
        try:
            answer_question = AnswerQuestion.objects.get(answer_questionnaire=aq.pk, question=validated_data['question'])
            answer_question.delete()
        except:
            pass

        answer_question = AnswerQuestion.objects.create(answer_questionnaire=aq, **validated_data)
        option = Option.objects.filter(question =validated_data['question'])

        #TODO Может надо кидать экспешн, если дают не корректный option. Сейчас сохраняют только корректный
        for answer_option_data in answer_options_data:
            for e in option:
                if e == answer_option_data['option']:
                    AnswerOption.objects.create(answer_question=answer_question, **answer_option_data)

        return answer_question

    def validate(self, data):
        if data['question'].question_type != 0 and data.get('text'):
            raise serializers.ValidationError("Question type not for text. Only Option.")

        if data['question'].question_type == 0 and len(data.get('answer_options'))>0:
            raise serializers.ValidationError("Question type not for options. Only text.")

        if data['question'].question_type == 1 and len(data.get('answer_options'))>1:
            raise serializers.ValidationError("Question type for only 1 options.")

        return data

    class Meta:
        model = AnswerQuestion
        fields = ('pk', 'question', 'text', 'answer_options')




