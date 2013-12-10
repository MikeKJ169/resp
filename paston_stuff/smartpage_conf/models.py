from django.db import models
from smartpages.models import SmartPage

class Configurator(models.Model):
    """
    We want to keep these options away from customers so only we can alter 
    them so they're in a seperate app with a OneToOne relation to a smartpage
    """
    smartpage = models.OneToOneField(SmartPage)
    editable = models.BooleanField(default=True, help_text='Can the customer edit it?')
    deletable = models.BooleanField(default=True, help_text='Can the customer delete it?')
    url = models.CharField('Url Catcher', max_length=255, blank=True, null=True)
    
    class Admin:
        list_display = ('smartpage','editable', 'deletable')

    def __unicode__(self):
        return u'%s' % self.smartpage
        
from django.db.models import signals
from django.dispatch import dispatcher
from smartpages.models import SmartPage

def add_smartpage_configurator(sender, signal, *args, **kwargs):
    created = kwargs.get('created')
    sp = kwargs.get('instance')
    if created:
        # Create a configuration object
        sp_conf = Configurator.objects.create(smartpage=sp)
        sp_conf.save()
    else:
        # Check there is a configuration object
        try:
            sp_conf = Configurator.objects.get(smartpage=sp)
        except Configurator.DoesNotExist:
            sp_conf = Configurator.objects.create(smartpage=sp)

dispatcher.connect(add_smartpage_configurator, signal=signals.post_save, sender=SmartPage)
