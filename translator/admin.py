import re

import requests
from django.conf.urls import url
from django.contrib import admin
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone

from .models import Lang, Record


class LangAdmin(admin.ModelAdmin):
    # Блокируем редактирование, создание, удаление языков
    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def get_readonly_fields(self, request, obj=None):
        return (list(self.readonly_fields) +
                [field.name for field in obj._meta.fields] +
                [field.name for field in obj._meta.many_to_many])

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass

    def delete_model(self, request, obj):
        pass

    def save_related(self, request, form, formsets, change):
        pass

    def get_ordering(self, request):
        return [Lower('description')]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = url(r'^load_langs/$', self.load_langs, name="custom_view")
        return [my_urls] + urls

    # Загружаем языки
    def load_langs(self, request):
        url = 'https://translate.yandex.net/api/v1.5/tr.json/getLangs'
        payload = dict(
            key='trnsl.1.1.20181103T080808Z.8633631b50e726f1.fc19df5d84cad2f7f4a4228b370d49bdaa44b8da',
            ui='ru',
        )
        try:
            r = requests.post(url, params=payload)
            if r.status_code == 200:
                langs = r.json()['langs']
                for code, desc in langs.items():
                    Lang.objects.get_or_create(
                        code=code,
                        defaults=dict(description=desc),
                    )
                dirs = r.json()['dirs']
                for dir in dirs:
                    m = re.match('(\w+)-(\w+)', dir)
                    if m:
                        left = Lang.objects.filter(code=m.group(1)).first()
                        right = Lang.objects.filter(code=m.group(2)).first()
                        if left and right:
                            left.can_translate_to.add(right)
            else:
                return HttpResponse(f'Произошла ошибка: код ответа='
                                    f'{r.status_code}, причина='
                                    f'{r.reason}',
                                    content_type='text/plain; charset=utf-8')
        except:
            return HttpResponse('Произошла непредвиденная ошибка',
                                content_type='text/plain; charset=utf-8')
        return redirect('/admin/translator/lang')


class RecordAdmin(admin.ModelAdmin):
    readonly_fields = [
        'created',
        'translated',
    ]

    # Загружаем перевод
    def translate(self, obj):
        url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
        payload = dict(
            key='trnsl.1.1.20181103T080808Z.8633631b50e726f1.fc19df5d84cad2f7f4a4228b370d49bdaa44b8da',
            lang=obj.destination_lang.code,
            format='html',
        )
        data = {'text': obj.source_text}
        r = requests.post(url, params=payload, data=data)
        if r.status_code == 200:
            obj.translated_text = r.json()['text'][0]
            obj.translated = timezone.now()
            obj.save()
        return r

    def response_add(self, request, obj, post_url_continue=None):
        if '_translate' in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = ''
            try:
                r = self.translate(obj)
            except:
                return HttpResponse('Произошла непредвиденная ошибка',
                                    content_type='text/plain; charset=utf-8')
            else:
                if r.status_code != 200:
                    return HttpResponse(f'Произошла ошибка: код ответа='
                                        f'{r.status_code}, причина='
                                        f'{r.reason}',
                                        content_type='text/plain; charset=utf-8')
        return super().response_add(request, obj)

    def response_change(self, request, obj):
        if '_translate' in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = ''
            try:
                r = self.translate(obj)
            except:
                return HttpResponse('Произошла непредвиденная ошибка',
                                    content_type='text/plain; charset=utf-8')
            else:
                if r.status_code != 200:
                    return HttpResponse(f'Произошла ошибка: код ответа='
                                        f'{r.status_code}, причина='
                                        f'{r.reason}',
                                        content_type='text/plain; charset=utf-8')
        return super().response_change(request, obj)


admin.site.register(Lang, LangAdmin)
admin.site.register(Record, RecordAdmin)