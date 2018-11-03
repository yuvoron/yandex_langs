from django.db import models
from django.utils import timezone

from ckeditor.fields import RichTextField


class Lang(models.Model):
    MAX_CODE_LENGTH = 10
    MAX_DESCRIPTION_LENGTH = 255

    code = models.CharField(
        max_length=MAX_CODE_LENGTH,
        verbose_name='Код языка',
        unique=True,
    )
    description = models.CharField(
        max_length=MAX_DESCRIPTION_LENGTH,
        verbose_name='Описание',
    )

    can_translate_to = models.ManyToManyField(
        'self',
        verbose_name='Переводим на',
        symmetrical=False,
        blank=True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Код языка'
        verbose_name_plural = 'Коды языков'


class Record(models.Model):
    MAX_TITLE_LENGTH = 255

    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name='Название',
        blank=True,
    )
    source_text = RichTextField(verbose_name='Исходный текст',)
    translated_text = RichTextField(
        verbose_name='Переведённый текст',
        blank=True,
    )
    destination_lang = models.ForeignKey(
        Lang,
        verbose_name='Язык перевода',
        related_name='dst_record_set',
        on_delete=models.PROTECT,
    )
    created = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания',
    )
    translated = models.DateTimeField(
        verbose_name='Дата перевода',
        blank=True,
        null=True
    )

    def publish(self):
        self.translated = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
