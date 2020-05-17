from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Questionnaire(models.Model):
    name = models.CharField(max_length=128, verbose_name='Наименование')
    date_begin = models.DateTimeField(verbose_name='Дата начала', auto_now_add=True, editable=False)
    date_end = models.DateTimeField(verbose_name='Дата окончания')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Опросник'
        verbose_name_plural = 'Опросники'

    def __str__(self):
        return self.name


class Question(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, related_name='questions', verbose_name='Опросник', on_delete=models.CASCADE)
    name = models.CharField(max_length=512, verbose_name='Текст вопроса')
    question_type = models.IntegerField(choices=((0, 'Text'),(1, 'Choices'), (2, 'Multi choices')))

    def __str__(self):
        return self.questionnaire.__str__()+'/'+ self.name.__str__()

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', verbose_name='Вопрос', on_delete=models.CASCADE)
    option = models.CharField(max_length=128, verbose_name='Вариант ответа')

    def __str__(self):
        return self.question.questionnaire.__str__()+'/'+ self.question.__str__()+'/'+self.option.__str__()

    class Meta:
        unique_together = ('question', 'option',)

class AnswerQuestionnaire(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, verbose_name='Опросник',  on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Дата прохождения',  auto_now_add=True, editable=False, )
    user = models.ForeignKey(User, editable=False, verbose_name='Пользователь', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Пройденный опрос'
        verbose_name_plural = 'Пройденные опросы'


class AnswerQuestion(models.Model):
    answer_questionnaire = models.ForeignKey(AnswerQuestionnaire,  related_name='answer_questions', verbose_name='Пройденный опрос', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='questions', verbose_name='Вопрос', on_delete=models.CASCADE)
    text = models.CharField(max_length=256,  blank=True, null=True, verbose_name='Ответ', default=None)

    class Meta:
        unique_together = ('answer_questionnaire', 'question')


class AnswerOption(models.Model):
    answer_question=models.ForeignKey(AnswerQuestion, verbose_name='Пройденный вопрос', related_name='answer_options', on_delete=models.CASCADE)
    option = models.ForeignKey(Option,  verbose_name='Вариант', on_delete=models.CASCADE)
    # question = models.PositiveIntegerField()
    #TODO Нужен составной ForeignKey на Option(option = Option.pk, question = Option.question), что бы отслеживать целостность

    class Meta:
        unique_together = ('answer_question', 'option')

