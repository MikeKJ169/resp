from django.db import models
from datetime import datetime
from django.db.models import permalink
from events.manager import EventsManager
from django.contrib.auth.models import User
from django.core.mail import send_mail

class Event(models.Model):


    title = models.CharField(max_length=100)
    short_desc = models.CharField(max_length=150)
    details = models.TextField()
    pub_date = models.DateTimeField('Date published', default=datetime.now)
    start_date = models.DateTimeField('Start date', default=datetime.now)
    end_date = models.DateTimeField('End date', default=datetime.now)
    expiry_date = models.DateField('Expiry Date', blank = True, null = True,help_text='Leave blank for no expiry',)
    picture = models.ImageField(upload_to='events_pictures', blank = True, null = True,)
    frontpage = models.BooleanField('Appear on frontpage',)
    priority = models.IntegerField(help_text='Small number => appears early in events listings', default=50)
    # slug is non-unique
    slug = models.TextField(max_length=50, blank=True, null=True)
    attending = models.ManyToManyField( User, null = True, blank = True )
    objects = EventsManager()

    def __unicode__(self):

        return self.title

    def get_absolute_url(self):

        return '/events/%s/' % str(self.id)
    
    def save(self):

        from django.template.defaultfilters import slugify
        from django.conf import settings
        self.slug=slugify(self.title)
        super(Event, self).save()
        send_mail("Event saved for you", "An event was saved for you", "web@paston.co.uk", [user.email for user in self.attending.all()] )


    def expired(self):

        if self.expiry_date and self.expiry_date < datetime.now().date():
            return 'Yes'
        else:
            return ''

    class Meta:

        ordering = ['priority', '-pub_date', ]

