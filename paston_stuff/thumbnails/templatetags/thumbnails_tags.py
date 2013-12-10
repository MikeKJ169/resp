""" image related filters """

##################################################
## DEPENDENCIES ##

from django import template
#from django.core.template import TemplateSyntaxError, Node, register_tag
from paston_stuff.thumbnails.utils import make_thumbnail, get_image_size

##################################################
## FILTERS ##

def thumbnail(url, args=''):
    """ Returns thumbnail URL and create it if not already exists.

.. note:: requires PIL_,
    if PIL_ is not found or thumbnail can not be created returns original URL.

.. _PIL: http://www.pythonware.com/products/pil/

Usage::

    {{ url|thumbnail:"width=10,height=20" }}
    {{ url|thumbnail:"width=10" }}
    {{ url|thumbnail:"height=20" }}
    {{ url|thumbnail:"maxwidth=100,maxheight=80" }}

Parameters:

width
    new image width

height
    new image height

maxwidth, maxheight
    If these are supplied the image will be proportionally resized to fit
    the boundary supplied by maxwidth and maxheight

Thumbnail file is saved in the same location as the original image
and his name is constructed like this::

    %(dirname)s/%(basename)s_t[_w%(width)d][_h%(height)d].%(extension)s

or if only a width is requested (to be compatibile with admin interface)::

    %(dirname)s/%(basename)s_t%(width)d.%(extension)s

"""
    
    kwargs = {}
    if args:
        if ',' not in args:
            # ensure at least one ','
            args += ','
        for arg in args.split(','):
            arg = arg.strip()
            if arg == '': continue
            kw, val = arg.split('=', 1)
            kw = kw.lower()
            try:
                val = int(val) # convert all ints
            except ValueError:
                raise template.TemplateSyntaxError, "thumbnail filter: argument %r is invalid integer (%r)" % (kw, val)
            kwargs[str(kw)] = val
        # for
    #
    
    if ('width' not in kwargs) and ('height' not in kwargs) and ('maxwidth' not in kwargs) and ('maxwidth' not in kwargs):
        raise template.TemplateSyntaxError, "thumbnail filter requires arguments (width and/or height)"
    if (('maxwidth' in kwargs) and ('maxheight' not in kwargs)) or (('maxheight' in kwargs) and ('maxwidth' not in kwargs)):
        raise template.TemplateSyntaxError, "thumbnail filter: if either maxwidth or maxheight is supplied then both must be supplied"

    ret = make_thumbnail(url, **kwargs)
    if ret is None:
        return url
    else:
        return ret
#

def image_width(url):
    """ Returns image width.

Usage:
    {{ url|image_width }}
"""
    
    width, height = get_image_size(url)
    return width
#

def image_height(url):
    """ Returns image height.

Usage:
    {{ url|image_width }}
"""
    
    width, height = get_image_size(url)
    return height
#

##################################################
## FILTER REGISTRATION ##

register = template.Library()

register.filter('thumbnail', thumbnail)
register.filter('image_width', image_width)
register.filter('image_height', image_height)
