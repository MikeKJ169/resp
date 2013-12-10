from django.template import loader, RequestContext
#from django.utils.translation import ugettext as _
#from django.db import models
from django.views.decorators.cache import never_cache
#from django.shortcuts import get_object_or_404
from django.core.exceptions import ImproperlyConfigured #, PermissionDenied
from django.http import Http404, HttpResponse #, HttpResponseRedirect
#from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.models import LogEntry #, ADDITION, CHANGE #, DELETION
if not LogEntry._meta.installed:
    raise ImproperlyConfigured, "You'll need to put 'django.contrib.admin' in your INSTALLED_APPS setting before you can use the admin application."

#from django.contrib.contenttypes.models import ContentType
from smartpages.models import SmartPage, Category
#from django.http import Http404

def smartpage_preview(request):
    t = loader.get_template('smartpages/preview.html')
    c = RequestContext(request, {
        'meta_title': 'Page preview',
        'content': '{$content}',
    })
    return HttpResponse(t.render(c))

def get_urlparts(url):

    """
    Strip leading / trailing slashes and smash up the url.
    """

    if url.startswith('/'):
        url = url[1:]
    if url.endswith('/'):
        url = url[0:-1]
    urlparts=url.split('/')
    return urlparts

def make_breadcrumbs(url):
    urlparts=get_urlparts(url)
    breadcrumbs=''
    i=0
    for urlpart in urlparts:
        c=Category.objects.filter(slug=urlpart)
        if len(c)==0:
            try:
                p=SmartPage.objects.get(slug=urlpart)
            except SmartPage.DoesNotExist:
                raise Http404
        else:
            p=c[0]
        if i<len(urlparts)-1:
            breadcrumbs+='&raquo; <a href="%s">%s</a> ' % (p.get_absolute_url(), p.name)
        else: breadcrumbs+="&raquo; "+p.name
        i+=1
    return breadcrumbs

@never_cache
def smartpage(request, url):
    """
    Models: `smartpages.smartpages`
    Templates: Uses the template defined by the ``template_name`` field,
        or `smartpages/default` if template_name is not defined.
    """

    DEFAULT_TEMPLATE = 'smartpages/default.html'
    template_list=[DEFAULT_TEMPLATE,]

    urlparts=get_urlparts(url)
    slug=urlparts[-1]


    cats=Category.objects.filter(slug=slug)
    # If it's a Category...
    if len(cats) >= 1:
        # We're serving a category index page
        cats=cats[:1]
        if cats[0].has_smartpage():
            sp = SmartPage.objects.get(slug=slug)
        else:
            template_list.insert(0,'smartpages/category_index.html')
            sp = cats[0]
            sp.content= None
    else:
        # If it's a Smartpage...
        try:
            sp = SmartPage.objects.get(slug=slug)
        except SmartPage.DoesNotExist:
            if request.user.has_perm('smartpages.add_smartpage'):
                c = RequestContext( request, {'pagename':request.path.split('/')[-2],})
                t = loader.get_template('smartpages/missing_page_admin.html')
                return HttpResponse(t.render(c))
            else:
                raise Http404
        
        template_list.insert(0,sp.template_name)
        cats = []
        for c in sp.categories.all():
            if c.slug_in_url:
                cats.append(c)
    # To do: Check the url parts are valid
    breadcrumbs=make_breadcrumbs(url)


    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
#    if f.registration_required and request.user.is_anonymous():
#        from django.views.auth.login import redirect_to_login
#        return redirect_to_login(request.path)

    t = loader.select_template(template_list)
    try: 
        featureboxes = sp.featurebox_set.order_by('priority')
    except:
        featureboxes = ( )
    c = RequestContext( request, {
        'smartpage_id': int(sp.id),
        'breadcrumbs':breadcrumbs,
        'parent_cats': cats,
        'smartpage_slug': slug,
        'title': sp.name,
        'content': sp.content,
        'meta_title': sp.meta_title,
        'meta_desc': sp.meta_desc,
        'meta_keywords': sp.meta_keywords,
        'featureboxes': featureboxes,
    })
    return HttpResponse(t.render(c))


class OhLook( NameError ):
    pass
