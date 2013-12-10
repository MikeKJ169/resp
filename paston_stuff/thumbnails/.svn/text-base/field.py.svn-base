#from django.db.models.fields import ImageField
from django.core.meta.fields import ImageField

class ImageWithThumbnailField(ImageField):
    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, **kwargs):
        super(ImageWithThumbnailField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)

    def get_internal_type(self):
        return 'ImageField'
    
    def save_file(self, new_data, new_object, original_object, change, rel):
        super(ImageWithThumbnailField, self).save_file(new_data, new_object, original_object, change, rel)
#        if change:
        url = getattr(new_object, 'get_%s_url' % self.name)()
        from thumbnails.utils import make_thumbnail, _remove_thumbnails
        _remove_thumbnails(url) # clear all of the old thumbnails
        make_thumbnail(url, width=150) # make admin thumbnail
