from django.db import models
from django.utils.translation import gettext_lazy as _
#from django.utils.encoding import force_unicode
from django.core.exceptions import PermissionDenied
#from util import delete_from_admin_list

#TODO: Replace regex validator


class Category(models.Model):
    slug = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    name = models.CharField(max_length=200)
    parent= models.ForeignKey('self', blank=True, null=True, related_name='child')

    meta_title = models.CharField(max_length=100, null=True, blank=True)
    meta_desc = models.CharField(max_length=250, null=True, blank=True)
    meta_keywords = models.CharField(max_length=250, null=True, blank=True)
    priority = models.IntegerField(help_text='Small number => appears early in lists', default=50)

    slug_in_url=models.BooleanField(default=True,help_text="Don't change this unless you know what you're doing!",)
    #remove = delete_from_admin_list
    #remove.allow_tags = True

    class Meta:
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return "%s -- %s" % (self.slug, self.name)

    def save(self):
        from smartpages.models import Category
        from django.template.defaultfilters import slugify

#        # Check we're not our own parent (even if we are from Norfolk):
#        try:
#        if self.id and self.parent and int(self.id)==int(self.parent.id):
#            raise PermissionDenied
#        except ValueError:
#            pass

        # Check we're not creating a hideous server-eating infinite loop
        p = self
        seen_ids=[]
        while p.parent:
            if p.id:
                seen_ids.append(int(p.id))
            if int(p.parent.id) in seen_ids:
                raise PermissionDenied
            p = p.parent

        slug=slugify(self.name)
        # Check for duplicate slugs and append a unique number if necessary
        dupes=Category.objects.filter(slug=slug)
        if self.id:
            dupes = dupes.exclude(id=self.id)
        if (dupes.count()==0):
            self.slug=slug
            super(Category, self).save()
            return
        i=2
        while(True):
            dupes=Category.objects.filter(slug='%s-%s' % (slug,str(i)))
            if self.slug: dupes=dupes.exclude(id=self.id)
            if dupes.count() == 0: break
            i+=1
    
        self.slug='%s-%s' % (slug,str(i))
        super(Category, self).save()

    def get_absolute_url(self):
        p=self
        pid=p.parent_id
        url='/'+p.slug+'/'
        while (pid):
            p=p.parent
            if p.slug_in_url:
                url= '/'+p.slug+url
            pid=p.parent_id
        return url


    def has_smartpage(self):
        from smartpages.models import SmartPage
        p = SmartPage.objects.filter(slug = self.slug)
        return len(p) > 0
        
    def get_child_cats_and_objects(self):
        from smartpages.utils import get_list_of_child_categories_and_objects
        #return get_list_of_child_categories_and_objects('smartpages', 'SmartPage', self.slug)
        listout = get_list_of_child_categories_and_objects('smartpages', 'SmartPage', cat_slug=self.slug) + get_list_of_child_categories_and_objects('smartpages', 'MenuLink', cat_slug=self.slug)
        listout.sort(lambda f, s: cmp(f['priority'], s['priority']))
        return listout




class MenuLink( models.Model ):
    name = models.CharField( max_length = 255 )
    slug = models.CharField( "URL", max_length = 255 )
    priority = models.IntegerField(help_text='Small number => appears early in lists',default=50,)
    categories = models.ManyToManyField( Category, null = True, blank = True )
    new_window = models.BooleanField()
    #remove = delete_from_admin_list
    #remove.allow_tags = True
    class Admin:
        pass
    def __unicode__( self ):
        return self.name
    def get_absolute_url( self ):
        return self.slug 


class SmartPage(models.Model):
    slug = models.CharField(max_length=100, unique=True, null = True, blank=True, db_index=True)
    name = models.CharField(max_length=200)
    content = models.TextField()
#    under_content = models.TextField(null=True, blank=True)
    meta_title = models.CharField(max_length=100, blank=True)
    meta_desc = models.CharField(max_length=250, blank=True)
    meta_keywords = models.CharField(max_length=250, blank=True)
    priority = models.IntegerField( default=50 )
    template_name = models.CharField(_('template name'), max_length=70, blank=True )

    # For the tinymce image uploader:
    editor_timestamp=models.IntegerField( )
    editor_uniqid=models.CharField(max_length=8)

    # For menus, sections etc:
    categories = models.ManyToManyField(Category, null=True, blank=True)
    #remove = delete_from_admin_list
    def page_link(self):
        return '<a href="%s">Go to page</a>' % self.get_absolute_url()
    page_link.allow_tags = True

    class Meta:
        ordering=('priority',)

    def __unicode__(self):
        return "%s -- %s" % (self.slug, self.name)

    def get_absolute_url(self):
        url=self.slug+'/'
        cats=self.categories.all()
        for cat in cats:
            if cat.slug_in_url:
                url=cat.get_absolute_url()+url
                return url
        
        return '/'+url

    def save(self):
        from django.conf import settings
        if 'paston_stuff.smartpage_conf' in settings.INSTALLED_APPS:
            from smartpage_conf.models import Configurator
            try:
                sp_conf = Configurator.objects.get(smartpage=self)
            except Configurator.DoesNotExist:
                sp_conf = None
        else:
            sp_conf = None
        
        if sp_conf == None or sp_conf.editable:
            from thumbnails.utils import make_thumbnail
            from smartpages.models import SmartPage
            from django.template.defaultfilters import slugify
            import string, re
            
            # Make resized versions of any required images
            imgpattern = re.compile(r'(<\s*img\s+[^>]*src=["\'])([^"]+)(["\']\s*[^>]*/\s*>)', re.IGNORECASE)
            dimpattern=re.compile(r'(width|height)\s*=\s*["\']?([0-9]+)["\']', re.IGNORECASE)
            imgmatches = imgpattern.findall(self.content)
            for imgmatch in imgmatches:
                startbit = imgmatch[0]
                img_url = imgmatch[1]
                endbit = imgmatch[2]
                if img_url.startswith('http'):
                    continue
                
                dimmatches=dimpattern.findall(startbit+endbit)
                dim={'width':None, 'height':None}
                for dimmatch in dimmatches:
                    dim[dimmatch[0]]=int(dimmatch[1])
                    
                # Get the original, unresized url of the image:
                matches=re.match(r'(.*)_t_w[0-9]+_h[0-9]+(\.[a-zA-Z]+)$', img_url)
                if matches: orig_img_url=matches.group(1)+matches.group(2)
                else: orig_img_url=img_url
                
                # make_thumbnail......
                if (dim['width'] and dim['height']):
                    sized_url=make_thumbnail(orig_img_url, int(dim['width']), int(dim['height']))
                else:
                    sized_url=orig_img_url
                    
                try:
                    self.content=string.replace(self.content,startbit+orig_img_url+endbit, startbit+sized_url+endbit)
                except TypeError:
                    pass

            # Turn the name into a slug and make ensure it's unique:
            slug=slugify(self.name)
    #        dupes=SmartPage.get_count(slug__exact=slug, id__ne=self.id)
            dupes=SmartPage.objects.filter(slug=slug)
            if self.id:
                dupes = dupes.exclude(id=self.id)
            if dupes.count()==0:
                self.slug=slug
            else:
                i=2
                while True:
                    dupes=SmartPage.objects.filter(slug='%s-%s' % (slug,str(i)))
                    if self.slug: dupes=dupes.exclude(id=self.id)
                    if dupes.count() == 0: break
                    i+=1
                
    #            while (SmartPage.get_count(slug__exact=slug+str(i), id__ne=self.id)>0):
    #                i+=1
                self.slug='%s-%s' % (slug,str(i))
            super(SmartPage, self).save()
            
            from smartpages.models import Image
            import re#, glob
            
            # Get rid of images assigned to the page but not appearing in the html
            for im in self.image_set.all():
                m=re.match(r'(?P<basename>.*)(?P<extension>\.[a-zA-Z]+)$', im.picture.url)
                if m:
                    bits=m.groupdict()
                    match=re.search(r'%s[_twh0-9]*%s' % (bits['basename'], bits['extension']), self.content)
                    
                    if (not match):
                        im.delete()
                        
            # Assign images added under the editor id to the page
            for im in Image.objects.filter(editor_uniqid=self.editor_uniqid):
                im.smartpage_id=self.id
                im.save()
            Image.objects.cleanup()
            
    def delete(self):
        from django.conf import settings
        if 'paston_stuff.smartpage_conf' in settings.INSTALLED_APPS:
            try:
                from smartpage_conf.models import Configurator
                try:
                    sp_conf = Configurator.objects.get(smartpage=self)
                except Configurator.DoesNotExist:
                    sp_conf = None
            except ImportError:
                sp_conf = None
        else:
            sp_conf = None
        
        if sp_conf == None or sp_conf.deletable:
            super(SmartPage, self).delete()


class ImageManager(models.Manager):
    def cleanup(self):
        # Delete old images that aren't assigned to any page
        import time
        from smartpages.models import Image
        timeout=1000*60*60*24 #1 day
        for deadim in Image.objects.filter(smartpage__isnull = True, editor_timestamp__lt = 1000*time.time()-timeout):
            deadim.delete()

class Image(models.Model):
    picture=models.ImageField(upload_to='smartpage_pics')
    smartpage=models.ForeignKey(SmartPage, null=True, blank=True, )
    editor_timestamp=models.IntegerField()
    editor_uniqid=models.CharField(max_length=8,)
    objects=ImageManager()

    def __unicode__(self):
        # print dir(self.picture)
        return self.picture.url

    # Get rid of old thumbnails:
    # To do...

#class FeatureBox(models.Model):
#    smartpage = models.ForeignKey(SmartPage, help_text='The page you\'d like this feature to appear on.')
#    priority = models.IntegerField(help_text="The lower the value entered the higher in the list the project will appear.") 
#    link = models.CharField(max_length=200, help_text='The internal url of the feature box.') 
#    picture = models.FileField(upload_to='smartpage_pics', blank=True, null=True, help_text='A picture for the feature box.') 
#    class Meta:
#        verbose_name_plural="Featureboxes"
#    
#    def __unicode__(self): 
#        return self.link
