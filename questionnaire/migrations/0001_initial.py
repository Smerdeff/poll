# Generated by Django 2.2.10 on 2020-05-18 21:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=128)),
                ('date_begin', models.DateField(auto_now_add=True, help_text='Дата начала')),
                ('date_end', models.DateField(help_text='Дата окончания')),
                ('description', models.TextField(blank=True, help_text='Описание', null=True)),
            ],
            options={
                'verbose_name': 'Опросник',
                'verbose_name_plural': 'Опросники',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Текст вопроса', max_length=512)),
                ('question_type', models.IntegerField(choices=[(0, 'Text'), (1, 'Choices'), (2, 'Multi choices')])),
                ('questionnaire', models.ForeignKey(help_text='Анкета', on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='questionnaire.Questionnaire')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.CharField(help_text='Вариант ответа', max_length=128)),
                ('question', models.ForeignKey(help_text='Вопрос', on_delete=django.db.models.deletion.CASCADE, related_name='options', to='questionnaire.Question')),
            ],
            options={
                'unique_together': {('question', 'option')},
            },
        ),
        migrations.CreateModel(
            name='AnswerQuestionnaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Дата прохождения')),
                ('questionnaire', models.ForeignKey(help_text='Опросник', on_delete=django.db.models.deletion.CASCADE, to='questionnaire.Questionnaire')),
                ('user', models.ForeignKey(editable=False, help_text='Пользователь', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Пройденный опрос',
                'verbose_name_plural': 'Пройденные опросы',
            },
        ),
        migrations.CreateModel(
            name='AnswerQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, default=None, help_text='Ответ', max_length=256, null=True)),
                ('answer_questionnaire', models.ForeignKey(help_text='Пройденный опрос', on_delete=django.db.models.deletion.CASCADE, related_name='answer_questions', to='questionnaire.AnswerQuestionnaire')),
                ('question', models.ForeignKey(help_text='Вопрос', on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='questionnaire.Question')),
            ],
            options={
                'unique_together': {('answer_questionnaire', 'question')},
            },
        ),
        migrations.CreateModel(
            name='AnswerOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_question', models.ForeignKey(help_text='Пройденный вопрос', on_delete=django.db.models.deletion.CASCADE, related_name='answer_options', to='questionnaire.AnswerQuestion')),
                ('option', models.ForeignKey(help_text='Вариант', on_delete=django.db.models.deletion.CASCADE, to='questionnaire.Option')),
            ],
            options={
                'unique_together': {('answer_question', 'option')},
            },
        ),
    ]
