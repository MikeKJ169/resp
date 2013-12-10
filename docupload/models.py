from django.db import models
from django.contrib.sites.models import Site
from django.conf import settings

SITE_ID = settings.SITE_ID
MEDIA_ROOT = settings.MEDIA_ROOT

class Doc(models.Model):
    """
    Model for Documents
    """
    name = models.CharField(max_length=255, help_text='A name to remind you what the document contains.')
    document = models.FileField(upload_to='docs')
    
    def url(self):
        return '/media/%s' % (self.document)
    
    def link(self):
        return '<a href="http://%s/media/%s" onclick="window.open(this.href,\'_blank\');return false;">Click here to preview Document</a>' % (Site.objects.get(id=SITE_ID), self.document)
    link.allow_tags = True

    def __unicode__(self):
        return self.name
        
    def delete(self):
        import os
        if os.path.exists(MEDIA_ROOT+self.document) and not os.path.isdir(MEDIA_ROOT+self.document) and self.document != "." and self.document != "..":
            os.remove(MEDIA_ROOT+self.document)
        super(Doc, self).delete()
