from django.contrib import admin
from events.models import Event
from django import forms
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode

class EventForm( forms.ModelForm ):
    pass

class EventAdmin( admin.ModelAdmin ):
    ordering = ['priority', '-pub_date', ]
    list_display = ('title', 'short_desc', 'pub_date', 'start_date', 'expiry_date', 'expired', 'priority', 'frontpage')
    list_filter = ['pub_date']
    search_fields = ['title', 'short_desc', 'details',]
    date_hierarchy = 'pub_date'
    fieldsets = (
        ('Simple Details', {'fields': ('title','short_desc',)}),
        ('Extra Detail', {'fields': ('details','picture','attending')}),
        ('Date information', {'fields': ('pub_date','start_date','end_date','expiry_date',)}),
        ('Display info', {'fields': ('priority','frontpage',)}),
        )
    class Media:
        js = (
        '../media-tiny_mce/tiny_mce.js',
        '../media/js/editor.js',
        )
    

admin.site.register( Event, EventAdmin )





    
