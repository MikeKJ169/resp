## from django.db.models import signals
## from django.dispatch import dispatcher
## from django.db import connection

## # This is annoying - at the time of writing it only works if the
## # project name is included in the import spec
## from paston_stuff.smartpages import models as smartpages_app

## def fix_table(sender, signal, *args, **kwargs):
##     """
##     Fix up fields that django makes as ints and need to be bigints.
##     Hopefully one day django will have a bigint field and this will go away
##     """
##     print "Fixing smartpages table..."
##     connection.cursor().execute("ALTER TABLE `smartpages_smartpage` CHANGE `editor_timestamp` `editor_timestamp` BIGINT(22) NULL DEFAULT NULL")
##     connection.cursor().execute("ALTER TABLE `smartpages_image` CHANGE `editor_timestamp` `editor_timestamp` BIGINT(22) NULL DEFAULT NULL")
##     print "...fixed"

## dispatcher.connect( fix_table, signal=signals.post_syncdb, sender=smartpages_app)
