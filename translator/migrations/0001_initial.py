# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-03 14:25
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='Код языка')),
                ('description', models.CharField(max_length=255, verbose_name='Описание')),
                ('can_translate_to', models.ManyToManyField(blank=True, to='translator.Lang', verbose_name='Переводим на')),
            ],
            options={
                'verbose_name': 'Код языка',
                'verbose_name_plural': 'Коды языков',
            },
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Название')),
                ('source_text', ckeditor.fields.RichTextField(verbose_name='Исходный текст')),
                ('translated_text', ckeditor.fields.RichTextField(blank=True, verbose_name='Переведённый текст')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('translated', models.DateTimeField(blank=True, null=True, verbose_name='Дата перевода')),
                ('destination_lang', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dst_record_set', to='translator.Lang', verbose_name='Язык перевода')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
    ]
