from django.db import models
from datetime import datetime
from django.db.models import permalink
from news.manager import NewsManager

class NewsItem(models.Model):
    title = models.CharField(max_length=100)
    short_desc = models.CharField(max_length=150)
    details = models.TextField()
    pub_date = models.DateTimeField('date published', default=datetime.now)
    expiry_date = models.DateField('Expiry Date', blank = True, null = True,help_text='Leave blank for no expiry',)
    picture = models.ImageField(upload_to='news_pictures', blank = True, null = True,)
    frontpage = models.BooleanField('Appear on frontpage',)
    priority = models.IntegerField(help_text='Small number => appears early in news listings', default=50)
    # slug is non-unique
    slug = models.TextField(max_length=50, blank=True, null=True)
    
    objects = NewsManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/news/%s/' % str(self.id)
    
    def save(self):
        from django.template.defaultfilters import slugify
        self.slug=slugify(self.title)
        super(NewsItem, self).save()

    def expired(self):
        if self.expiry_date and self.expiry_date < datetime.now().date():
            return 'Yes'
        else:
            return ''

    class Meta:
        ordering = ['priority', '-pub_date', ]

