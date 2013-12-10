from django import template

from news.models import NewsItem
from datetime import datetime

register = template.Library()

#class NewsFlashNode(template.Node):
#    def __init__(self, title='Latest news'):
#        self.title=title
#
#    def render(self, context):
#        from django.core.meta import Q
#        latest_news_list = newsitems.get_list(complex=(Q(expiry_date__gte=datetime.now()) | Q(expiry_date__isnull=True)), order_by=['-priority','-pub_date',], limit=5)
#        
#        if len(latest_news_list) < 1:
#            return ''
#
#        content=''
#        content+='<h4>%s</h4>' % self.title
#        for p in latest_news_list:
#            content += '<p><a href="/news/'+str(p.id)+'">'+p.title+'</a></p>'
#        return '<div class="newsflashbox">'+content+'</div>'
##        return '<br />'.join([p.title for p in latest_news_list])
#
#def do_newsflash(parser, token):
#    from tagsnfilters import parse_templatetagtoken
#
#    kwargs=parse_templatetagtoken(token)
#    return NewsFlashNode(**kwargs)
#register.tag('newsflash', do_newsflash)

#def test_tag(somearg='abc', someotherarg='def'):
#    return 'test results: %s' % somearg
#test_tag = register.simple_tag(test_tag)

def latest_news(max_items=8):
    latest_news_list = NewsItem.objects.latest()[:max_items]
    return { 'latest_news_list' : latest_news_list, }
latest_news=register.inclusion_tag('news/latest_news.html')(latest_news)
