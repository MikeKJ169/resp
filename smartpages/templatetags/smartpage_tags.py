from django import template
from django.conf import settings
from smartpages.utils import get_list_of_child_categories_and_objects
from django.template import resolve_variable
from django.utils.html import escape
dictlist_set = lambda x: [ i[0] for i in zip( x, [not x[y] in x[y+1:] for y in range(len(x))] ) if i[1] ]

import re

MEDIA_ROOT=settings.MEDIA_ROOT
MEDIA_URL=settings.MEDIA_URL

register = template.Library()

def getit(li, id, x=False):
    for i in li:
        if x: return i
        elif i['id'] == int(id): x=True

#def get_smartpage( parser, token ):
#    """Directly retrieve a smartpage by its slug - useful for generic views and stuff. warning: does not raise a 404 if the smartpage does not exist."""
#    args = token.contents.split()
#    if len( args ) != 4:
#        raise template.TemplateSyntaxError, """Incorrect input - think more along the lines of get_smartpage smartpage as variable."""
#    if args[2] != 'as':
#        raise template.TemplateSyntaxError, """Incorrect input - think more along the lines of get_smartpage smartpage as variable."""
#    return SmartPageSpewNode( args[1], args[3] )


class HtmlListItemsNode(template.Node):
    def __init__(self, list_name ):
        self.list_name=list_name
    
    def render(self, context):
        #from urllib import quote
        #from smartpages.models import MenuLink
        listname=resolve_variable(self.list_name, context)
        mylist=get_list_of_child_categories_and_objects('smartpages', 'SmartPage', cat_slug=listname) + get_list_of_child_categories_and_objects('smartpages', 'MenuLink', cat_slug=listname)
        mylist.sort(lambda f, s: cmp(f['priority'], s['priority']))
        mylist = dictlist_set(mylist)
        if not mylist:
            return ''
        content=''
        target=''
        for e in mylist:
            if e['childtype'] == "MenuLink" and e['object'].new_window:
                target =   " target=\"_blank\" "
            if hasattr(context, "smartpage_slug"):
                slug=context['smartpage_slug']
            else:
                slug=""
            content+="<li><a href=\""+e['url']+"\""+target+" class=\""+e['object'].slug+[' noncurrent_link',' zcurrent_link'][slug==e['object'].slug]+"\" >"+escape(e['name'])+"</a></li>\n"

        return content

def do_htmllistitems(parser, token):
        tag_name, arg = token.contents.split(None, 1)
        return HtmlListItemsNode(arg)

class ReturnContextListItemsNode(template.Node):
	"""
	For when you just want a bare python list of items in a smartpage category.
	
	Usage:
		
		{% smartpage_list "main-menu" as pages %}
	
	Will give you all pages in the "main-menu" category as context variable 'pages'
	TODO: cut down returned output to necessary things
	"""
	def __init__(self, category, var_name):
		self.category = category
		self.var_name = var_name
	def render(self, context):
            listout = get_list_of_child_categories_and_objects('smartpages', 'SmartPage', cat_slug=self.category) + get_list_of_child_categories_and_objects('smartpages', 'MenuLink', cat_slug=self.category)
            listout.sort(lambda f, s: cmp(f['priority'], s['priority']))
            context[self.var_name] = dictlist_set(listout)
            return ''

def do_smartpage_list(parser, token):
	try:
		tag_name, arg = token.contents.split(None, 1)
	except ValueError:
		raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents[0]
	m = re.search(r'(.*?) as (\w+)', arg)
	if not m:
		raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
	category, var_name = m.groups()
	if not (category[0] == category[-1] and category[0] in ('"', "'" )):
		template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
	return ReturnContextListItemsNode(category[1:-1], var_name)
	

register.tag('htmllistitems', do_htmllistitems)
register.tag('smartpage_list', do_smartpage_list)
#register.tag( 'get_smartpage', get_smartpage )
