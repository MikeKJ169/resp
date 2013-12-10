from django.contrib import admin
from news.models import NewsItem
from django import forms
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode

class NewsItemForm( forms.ModelForm ):
    pass

class NewsItemAdmin( admin.ModelAdmin ):
    ordering = ['priority', '-pub_date', ]
    list_display = ('title', 'short_desc', 'pub_date', 'expiry_date', 'expired', 'priority', 'frontpage')
    list_filter = ['pub_date']
    search_fields = ['title', 'short_desc', 'details',]
    date_hierarchy = 'pub_date'
    fieldsets = (
        ('Simple Details', {'fields': ('title','short_desc',)}),
        ('Extra Detail', {'fields': ('details','picture',)}),
        ('Date information', {'fields': ('pub_date','expiry_date',)}),
        ('Display info', {'fields': ('priority','frontpage',)}),
        )
    class Media:
        js = (
        '../media-tiny_mce/tiny_mce.js',
        '../media/js/editor.js',
        )
    

admin.site.register( NewsItem, NewsItemAdmin )





    
