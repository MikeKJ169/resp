from django.forms.widgets import TextInput

def delete_from_admin_list( self ):
    """ Add me to your model after your fields using:
    delete_from_admin_list = delete_from_admin_list
    then add 'delete_from_admin_list' to your list_display in admin.py """
    return """<a href="%s/delete/" class="deletelink">Delete</a></p>""" % ( self.pk )

class vDateField( TextInput ):
    def __init__( self, *args, **kwargs ):
        self.attrs={'class':"vDateField required"}
