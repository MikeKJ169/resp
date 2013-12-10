from django.conf.urls.defaults import patterns, include
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

if settings.LOCAL_DEV:
    urlpatterns = patterns('',
        (r'^media-tiny_mce/tiny_mce_gzip.php$', 'django.views.static.serve', {'document_root': '/var/www/tiny_mce_2_1_1', 'path':'tiny_mce.js',}),
        (r'^media-tiny_mce/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/www/tiny_mce_2_1_1', 'show_indexes':True}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
)
else:
    urlpatterns = patterns('')

urlpatterns += patterns('',
    (r'^r/', include('django.conf.urls.shortcut')), # For the 'View on site' button in the admin
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^', include('smartpages.urls')),
)

