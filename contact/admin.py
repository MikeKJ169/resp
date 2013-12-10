from django.contrib import admin
from contact.models import Type, Contact
from django import forms
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode

class TypeAdmin( admin.ModelAdmin ):
    pass

admin.site.register( Type, TypeAdmin )

class ContactAdmin( admin.ModelAdmin ):
    list_display = ('name', 'email', 'type',)
    class Media:
        js = (
            '/media-tiny_mce/tiny_mce.js',
            #'/media-tiny_mce/tiny_mce_gzip.php',
            '/media/js/editor.js',
        )

admin.site.register( Contact, ContactAdmin )
