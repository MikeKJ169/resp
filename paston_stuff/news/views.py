# Create your views here.
from news.models import NewsItem
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import Http404
from datetime import datetime, date
from django.template import RequestContext

def index(request):
    newsitems = NewsItem.objects.current()
    return render_to_response('news/index.html', {'newsitems': newsitems,}, context_instance=RequestContext(request))
    
def archive(request):
    newsitems = NewsItem.objects.archive()
    return render_to_response('news/index.html', {'newsitems' : newsitems}, context_instance=RequestContext(request))

def detail(request, news_id):
    n = get_object_or_404(NewsItem,pk=news_id)
    if n.pub_date > datetime.now():
        raise Http404
    if n.expiry_date and (n.expiry_date < date.today()):
        raise Http404
    return render_to_response('news/newsitem.html', {'newsitem': n,}, context_instance=RequestContext(request))
