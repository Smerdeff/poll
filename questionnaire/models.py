from django.db import models
from django.contrib.auth.models import User


# Create your models here.
QT_TEXT = 0
QT_CHOICES = 1
QT_MULTI_CHOICES = 2

class Questionnaire(models.Model):
    """
        Анкета
    """
    name = models.CharField(max_length=128, help_text='Наименование')
    date_begin = models.DateField(help_text='Дата начала', auto_now_add=True, editable=False)
    date_end = models.DateField(help_text='Дата окончания')
    description = models.TextField(blank=True, null=True, help_text='Описание')

    # class Meta:
    #     verbose_name = 'Опросник'
    #     verbose_name_plural = 'Опросники'

    def __str__(self):
        return self.name


class Question(models.Model):
    """
        Вопрос в анкете
    """
    questionnaire = models.ForeignKey(Questionnaire, related_name='questions', help_text='Анкета',
                                      on_delete=models.CASCADE)
    name = models.CharField(max_length=512, help_text='Текст вопроса')
    question_type = models.IntegerField(choices=((QT_TEXT, 'Text'), (QT_CHOICES, 'Choices'), (QT_MULTI_CHOICES, 'Multi choices')), help_text='Тип вопроса')

    def __str__(self):
        return self.questionnaire.__str__() + '/' + self.name.__str__()


class Option(models.Model):
    """
        Варианты ответа
    """
    question = models.ForeignKey(Question, related_name='options', help_text='Вопрос', on_delete=models.CASCADE)
    option = models.CharField(max_length=128, help_text='Вариант ответа')

    def __str__(self):
        return   self.question.__str__() + '/' + self.option.__str__()

    class Meta:
        unique_together = ('question', 'option',)


class AnswerQuestionnaire(models.Model):
    """
        Прохождение анкеты
    """
    questionnaire = models.ForeignKey(Questionnaire, help_text='Опросник', on_delete=models.CASCADE)
    created_at = models.DateTimeField(help_text='Дата прохождения', auto_now_add=True, editable=False, )
    user = models.ForeignKey(User, editable=False, help_text='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return self.questionnaire.name + ' от ' + self.created_at.__str__() + '(' + self.user.__str__() + ')'

    class Meta:
        verbose_name = 'Пройденная анкета'


class AnswerQuestion(models.Model):
    """
        Ответы на вопросы в прохождении анкеты
    """
    answer_questionnaire = models.ForeignKey(AnswerQuestionnaire, related_name='answer_questions',
                                             help_text='Пройденный опрос', on_delete=models.CASCADE)

    question = models.ForeignKey(Question, related_name='questions', help_text='Вопрос', on_delete=models.CASCADE)
    text = models.CharField(max_length=256, blank=True, null=True, help_text='Ответ', default=None)
    question_type = models.IntegerField(choices=((0, 'Text'), (1, 'Choices'), (2, 'Multi choices')))
    # questionnaire = models.PositiveIntegerField(help_text='Анкета')
    # TODO Возможно нужен составной ForeignKey на Question(question = Question.pk, questionnaire = Question.questionnaire), что бы отслеживать целостность на уровене базы

    def __str__(self):
        return self.question.name +'/'+ self.answer_questionnaire.__str__()+'/'+self.answer_questionnaire_id.__str__()

    class Meta:
        unique_together = ('answer_questionnaire', 'question')
        verbose_name = 'Ответ на вопрос'


class AnswerOption(models.Model):
    """
        Ответы на вопросы при выборе
    """
    answer_question = models.ForeignKey(AnswerQuestion, help_text='Пройденный вопрос', related_name='answer_options',
                                        on_delete=models.CASCADE)
    option = models.ForeignKey(Option, help_text='Вариант', on_delete=models.CASCADE)

    # question = models.PositiveIntegerField(help_text='Вопрос')
    # TODO Возможно нужен составной ForeignKey на Option(option = Option.pk, question = Option.question), что бы отслеживать целостность на уровене базы

    class Meta:
        unique_together = ('answer_question', 'option')
        verbose_name = 'Ответ на вопрос с вариантами'
