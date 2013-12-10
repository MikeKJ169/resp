from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ncan/', include('ncan.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^r/', include('django.conf.urls.shortcut')),
    (r'^admin/', include(admin.site.urls)),
    (r'^contact-us/$', 'contact.views.contact'),
    (r'^contactreport/$', 'dl_reports.contact_report'),     
    (r'^', include('smartpages.urls')),
)
