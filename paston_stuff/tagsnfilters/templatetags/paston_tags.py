from django import template
from django.template import VariableDoesNotExist
from django.conf import settings
import os, re, string

MEDIA_ROOT=settings.MEDIA_ROOT
MEDIA_URL=settings.MEDIA_URL
register = template.Library()

def floatformatter(value):
	return '%0.2f' % value
		
def filesuffix(value):
    "Return everything after the last dot"
    return value[1+value.rfind('.'):]

def pathtourl(value):
    "Turn eg. /var/www/django/sitename/media/thingy.jpg into /media/thingy.jpg"
    if value.startswith(MEDIA_ROOT):
        return os.path.join(MEDIA_URL, value[len(MEDIA_ROOT):])
    else:
        return "Couldn't get path from value."

class SetContextVarNode(template.Node):
    def __init__(self, varname, nodelist):
        self.varname = varname
        self.nodelist=nodelist
    def render(self, context):
        context[self.varname] = self.nodelist.render(context)
        return self.nodelist.render(context)

def do_setvar(parser, token):
    """
    Capture content and set a context variable to the captured string
    """
    try:
        # Splitting by None == splitting by spaces.
        tag_name, format_string = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires an argument" % token.contents[0]
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    nodelist = parser.parse(('endsetvar',))
    parser.delete_first_token()
    return SetContextVarNode(format_string[1:-1], nodelist)

class PyImportNode(template.Node):
    """ Import a python variable """
    def __init__(self, import_spec):
        self.import_spec = import_spec

    def render(self, context):
        bits=self.import_spec.split('.')
        m = __import__('.'.join(bits[:-1]))
        m = __import__(bits[0])
        for i in bits[1:]:
            m = getattr(m, i)
        context[bits[-1]] = m
        return ''

def do_py_import(parser, token):
    """
    Capture content and set a context variable to the captured string
    """
    try:
        # Splitting by None == splitting by spaces.
        tag_name, import_spec = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires an argument" % token.contents[0]
    return PyImportNode(import_spec)

class DumpVarNode(template.Node):
    """
    Dump debug info about a variable into the console
    """
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        v = resolve_variable(self.var_name, context)
        print "Dumping context variable '%s':" % self.var_name
        print v
        print dir(v)
        return ''

def do_dump_var(parser, token):
    tag_name, var_name = token.contents.split(None, 1)
    return DumpVarNode(var_name)

def truncateurls(value, limit):
    limit = 30
    return do_truncateurls(value, trim_url_limit=int(limit))

def do_truncateurls(text, trim_url_limit=None):
    """
    Inspiration taken (read: stolen) from urlizetrunc. 
    This truncates existing urls to a given limit, like so:
	
    {{ data|truncateurls:60 }} - Truncates urls more than 60 characters long
    """
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (x[:limit] + (len(x) >=limit and '...' or ''))  or x
    link = re.compile(r'(a href=".*">)(.*)(</a)')
    re_splits = re.compile(r'(><)')

    lines = re_splits.split(text)
    for i, line in enumerate(lines):
        match =	link.match(line)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('http://') or middle.startswith('www'):
                middle = trim_url(middle)
            if lead + middle + trail != line:
                lines[i] = lead + middle + trail
    return ''.join(lines)

from django.template import Node, NodeList, Template, Context, resolve_variable

class IfContainsNode(Node):
    def __init__(self, var1, var2, nodelist_true, nodelist_false, negate):
        self.var1, self.var2 = var1, var2
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __repr__(self):
        return "<IfContainsNode>"

    def render(self, context):
        try:
            val1 = resolve_variable(self.var1, context)
        except VariableDoesNotExist:
            val1 = None
        if not (hasattr(val1, '__iter__') or isinstance(val1, basestring)):
            return self.nodelist_false.render(context)
        try:
            val2 = resolve_variable(self.var2, context)
        except VariableDoesNotExist:
            val2 = None
        if (self.negate and val2 not in val1) or (not self.negate and val2 in val1):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)

def do_ifcontains(parser, token, negate):
    """
    Output the contents of the block if the second argument is contained within the first argument

    Examples::

        {% ifcontains user.id comment.user_id %}
            ...
        {% endifcontains %}

        {% ifnotcontains user.id comment.user_id %}
            ...
        {% else %}
            ...
        {% endifnotcontains %}

    """
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes two arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfContainsNode(bits[1], bits[2], nodelist_true, nodelist_false, negate)

def ifcontains(parser, token):
    return do_ifcontains(parser, token, False)
ifcontains = register.tag(ifcontains)

register.filter('floatformatter',floatformatter)
register.filter('filesuffix',filesuffix)
register.filter('pathtourl',pathtourl)
register.tag('setvar', do_setvar)
register.tag('py_import', do_py_import)
register.tag('dump_var', do_dump_var)
register.filter('truncateurls', do_truncateurls)
