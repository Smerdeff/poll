from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Questionnaire(models.Model):
    """
        Анкета
    """
    name = models.CharField(max_length=128, help_text='Наименование')
    date_begin = models.DateTimeField(help_text='Дата начала', auto_now_add=True, editable=False)
    date_end = models.DateTimeField(help_text='Дата окончания')
    description = models.TextField(blank=True, null=True, help_text='Описание')

    class Meta:
        verbose_name = 'Опросник'
        verbose_name_plural = 'Опросники'

    def __str__(self):
        return self.name


class Question(models.Model):
    """
        Вопрос в анкете
    """
    questionnaire = models.ForeignKey(Questionnaire, related_name='questions', help_text='Анкета', on_delete=models.CASCADE)
    name = models.CharField(max_length=512, help_text='Текст вопроса')
    question_type = models.IntegerField(choices=((0, 'Text'),(1, 'Choices'), (2, 'Multi choices')))

    def __str__(self):
        return self.questionnaire.__str__()+'/'+ self.name.__str__()

class Option(models.Model):
    """
        Варианты ответа
    """
    question = models.ForeignKey(Question, related_name='options', help_text='Вопрос', on_delete=models.CASCADE)
    option = models.CharField(max_length=128, help_text='Вариант ответа')

    def __str__(self):
        return self.question.questionnaire.__str__()+'/'+ self.question.__str__()+'/'+self.option.__str__()

    class Meta:
        unique_together = ('question', 'option',)

class AnswerQuestionnaire(models.Model):
    """
        Прохождение анкеты
    """
    questionnaire = models.ForeignKey(Questionnaire, help_text='Опросник',  on_delete=models.CASCADE)
    created_at = models.DateTimeField(help_text='Дата прохождения',  auto_now_add=True, editable=False, )
    user = models.ForeignKey(User, editable=False, help_text='Пользователь', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Пройденный опрос'
        verbose_name_plural = 'Пройденные опросы'


class AnswerQuestion(models.Model):
    """
        Ответы на вопросы в прохождении анкеты
    """
    answer_questionnaire = models.ForeignKey(AnswerQuestionnaire,  related_name='answer_questions', help_text='Пройденный опрос', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='questions', help_text='Вопрос', on_delete=models.CASCADE)
    text = models.CharField(max_length=256,  blank=True, null=True, help_text='Ответ', default=None)

    class Meta:
        unique_together = ('answer_questionnaire', 'question')


class AnswerOption(models.Model):
    """
        Ответы на вопросы при выборе
    """
    answer_question=models.ForeignKey(AnswerQuestion, help_text='Пройденный вопрос', related_name='answer_options', on_delete=models.CASCADE)
    option = models.ForeignKey(Option,  help_text='Вариант', on_delete=models.CASCADE)
    # question = models.PositiveIntegerField(help_text='Вопрос')
    #TODO Нужен составной ForeignKey на Option(option = Option.pk, question = Option.question), что бы отслеживать целостность

    class Meta:
        unique_together = ('answer_question', 'option')

