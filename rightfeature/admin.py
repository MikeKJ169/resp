from django.contrib import admin
from rightfeature.models import Feature
from django import forms
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode

class FeatureAdmin( admin.ModelAdmin ):
    list_display = ('title', 'priority', 'link', 'external_link', 'box_text_color', 'box_bkgnd_color',)
    class Media:
        js = (
            '/media-tiny_mce/tiny_mce.js',
            #'/media-tiny_mce/tiny_mce_gzip.php',
            '/media/js/editor.js',
        )    

admin.site.register( Feature, FeatureAdmin )
