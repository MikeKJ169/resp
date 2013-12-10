from django.db import models
from datetime import datetime
from django.db.models import Q

class NewsManager(models.Manager):
    """
    Try and encapsulate the things we do with news in a manager
    """
    def frontpage(self):
        return self.filter( Q(frontpage_expiry_date__gt=datetime.now()) | Q(frontpage_expiry_date__isnull=True)).filter(frontpage_pub_date__lt=datetime.now()).order_by('frontpage_priority',)
    
    def current(self):
        return self.filter( Q(expiry_date__gt=datetime.now()) | Q(expiry_date__isnull=True)).filter(pub_date__lt=datetime.now()).order_by('priority','-pub_date')
        
    def archive(self):
        return self.filter( Q(expiry_date__lt=datetime.now()) | Q(expiry_date__isnull=True)).order_by('priority', '-pub_date')