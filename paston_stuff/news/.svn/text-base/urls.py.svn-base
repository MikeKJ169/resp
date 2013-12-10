from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'news.views.index', name="news-latest"),
    url(r'^archive/$', 'news.views.archive', name="news-archive"),
    url(r'^(?P<news_id>\d+)/$', 'news.views.detail', name="news-detail"),
) 
