from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^(?P<up_or_down>up|down)/(?P<content_type_id>[0-9]+)/(?P<object_id>[0-9]+)/$', 'alter_priority.views.alter_priority'),
)
 
