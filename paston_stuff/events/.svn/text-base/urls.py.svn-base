from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'events.views.index', name="events-latest"),
    url(r'^archive/$', 'events.views.archive', name="events-archive"),
    url(r'^calendar/(\d{4})/(\d{2})/(\d{2})/$', 'events.views.day', name="events-day"),
    url(r'^attend-event/(?P<event_id>\d+)/$', 'events.views.attend_event', name="events-attend"),
    # url(r'^unattend-event/(?P<event_id>\d+)/$', 'events.views.unattend_event', name="events-unattend"),
    url(r'^(?P<events_id>\d+)/$', 'events.views.detail', name="events-detail"),
) 
