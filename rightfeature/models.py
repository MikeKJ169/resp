from django.db import models
from smartpages.models import SmartPage


class Feature(models.Model):
    smartpage = models.ManyToManyField(SmartPage)
    title = models.CharField(max_length=50)
    image = models.FileField(upload_to='feature_images', null=True, blank=True, help_text='An image with grey backgrouund icon and tet will take preference over the title, if no image the title will be displayed')
    text = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=50, null=True, blank=True, help_text='if used do not forget the leading and trailing slashes')
    external_link = models.BooleanField(help_text='Check this if the link is external')
    priority = models.IntegerField(default=50)
    box_text_color  = models.CharField(max_length=6, null=True, blank=True, help_text='Enter the 6 character code of the hex color, do NOT enter the #')
    box_bkgnd_color = models.CharField(max_length=6, null=True, blank=True, help_text='Enter the 6 character code of the hex color, do NOT enter the #')

    def __unicode__(self):
        return self.title

