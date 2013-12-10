from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$', 'smartpages.views.smartpage', {'url':'/home/',}),
    (r'^smartpage-preview/$', 'smartpages.views.smartpage_preview'),
    (r'^(?P<url>.*)$', 'smartpages.views.smartpage'),
)

