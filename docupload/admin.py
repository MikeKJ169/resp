from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode
from docupload.models import Doc


class DocAdmin(admin.ModelAdmin):
    list_display = ('name', 'url',)

admin.site.register(Doc, DocAdmin)

