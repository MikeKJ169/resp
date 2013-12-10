from django.db import models

class Type( models.Model ):
    option = models.CharField(max_length=150)

    def __unicode__(self):
        return self.option

class Contact( models.Model ):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    type = models.ForeignKey(Type)
    content = models.TextField()

    def __unicode__(self):
        return "%s - %s" % (self.name, self.email)

