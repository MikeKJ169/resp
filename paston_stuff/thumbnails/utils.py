import os, urlparse, fnmatch
from django.conf import settings
from django.db.models.fields.files import ImageField
from django.core.cache import get_cache
import struct

MEDIA_ROOT=settings.MEDIA_ROOT
MEDIA_URL=settings.MEDIA_URL
 
# expire in 1h
image_cache = get_cache('locmem:///')

_FILE_CACHE_TIMEOUT = 60 * 60 * 60 * 24 * 31 # 1 month
_THUMBNAIL_GLOB = '%s_t*%s'

# check for PIL
try:
    import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def _get_thumbnail_path(path, width=None, height=None, maxwidth=None, maxheight=None, square=None):
    """ create thumbnail path from path and required width and/or height.
    
        thumbnail file name is constructed like this:
            <basename>_t_[w<width>][_h<height>].<extension>
    """
    
    # one of width/height or both of maxwidth/maxheight is required
    assert (width is not None) or (height is not None) or ((maxwidth is not None) and (maxheight is not None))

    basedir = os.path.dirname(path) + '/'
    base, ext = os.path.splitext(os.path.basename(path))
    
    # make thumbnail filename
    th_name = base + '_t'
    if square:
        th_name += '_sq'
    if (width is not None) and (height is not None):
        th_name += '_w%d_h%d' % (width, height)
    elif width is not None:
        th_name += '%d' % width # for compatibility with admin
    elif height is not None:
        th_name += '_h%d' % height

    if (maxwidth is not None) and (maxheight is not None):
        th_name += '_mw%d_mh%d' %(maxwidth, maxheight)

    th_name += ext
    
    return urlparse.urljoin(basedir, th_name)
#

def _get_path_from_url(url, root=MEDIA_ROOT, url_root=MEDIA_URL):
    """ make filesystem path from url """

    if url.startswith(url_root):
        url = url[len(url_root):] # strip media root url

    return os.path.normpath(os.path.join(root, url))
#

def _get_url_from_path(path, root=MEDIA_ROOT, url_root=MEDIA_URL):
    """ make url from filesystem path """

    if path.startswith(root):
        path = path[len(root):] # strip media root
    
    return urlparse.urljoin(root, path.replace('\\', '/'))
#

def _has_thumbnail(photo_url, width=None, height=None, maxwidth=None, maxheight=None, square=None, root=MEDIA_ROOT, url_root=MEDIA_URL):
    # one of width/height is required
    assert (width is not None) or (height is not None) or ((maxwidth is not None) and (maxheight is not None))

    return os.path.isfile(_get_path_from_url(_get_thumbnail_path(photo_url, width, height, maxwidth, maxheight, square), root, url_root))
#

def make_thumbnail(photo_url, width=None, height=None, maxwidth=None, maxheight=None, square=None, root=MEDIA_ROOT, url_root=MEDIA_URL):
    """ create thumbnail """
    
    # one of width/height is required
    assert (width is not None) or (height is not None) or ((maxwidth is not None) and (maxheight is not None))
    if not HAS_PIL: return None # no PIL - no thumbnail
    if not photo_url: return None

    th_url = _get_thumbnail_path(photo_url, width, height, maxwidth, maxheight, square)
    th_path = _get_path_from_url(th_url, root, url_root)
    photo_path = _get_path_from_url(photo_url, root, url_root)
    
    if _has_thumbnail(photo_url, width, height, maxwidth, maxheight, root, url_root):
        # thumbnail already exists
        if not (os.path.getmtime(photo_path) > os.path.getmtime(th_path)):
            # if photo mtime is newer than thumbnail recreate thumbnail
            return th_url
    
    # make thumbnail
    
    # get original image size
    orig_w, orig_h = get_image_size(photo_url, root, url_root)
    if (orig_w is None) and (orig_h) is None:
        # something is wrong with image
        return None
    
    # make proper size
    if (maxwidth is not None) and (maxheight is not None):
        currentratio=float(orig_w)/float(orig_h)
        newratio=float(maxwidth)/float(maxheight)
        if (newratio > currentratio):
            size=(orig_w*maxheight/float(orig_h),maxheight)
        else:
            size=(maxwidth,orig_h*maxwidth/float(orig_w))
    elif (width is not None) and (height is not None):
        if (orig_w == width) and (orig_h == height):
            # same dimensions
            return photo_url
        size = (width, height)
    elif width is not None:
        if orig_w == width:
            # same dimensions
            return None
        size = (width, orig_h)
    elif height is not None:
        if orig_h == height:
            # same dimensions
            return None
        size = [orig_w, height]

    size = [int(size[0]), int(size[1])]

#    try:
    img = Image.open(photo_path).copy()
    if square:
        from PIL import ImageOps
        img = ImageOps.fit(img, (min(*img.size),) * 2, Image.ANTIALIAS, 0, (.5, .5))
        ff=open( th_path + ".log", "w+" )
        ff.write("saved as a square thumbnail")
        ff.close()
    else:
        img.thumbnail(size, Image.ANTIALIAS)
        ff=open( th_path + ".log", "w+" )
        ff.write("saved as a normal thumbnail")
        ff.close()
    img.save(th_path)

#    except Exception, err:
#        # this goes to webserver error log#
#
#        import sys
#        print >>sys.stderr, '[MAKE THUMBNAIL] error %s for file %r' % (err, photo_url)
#        return photo_url

    return th_url
#

def _remove_thumbnails(photo_url, root=MEDIA_ROOT, url_root=MEDIA_URL):
    if not photo_url: return # empty url

    file_name = _get_path_from_url(photo_url, root, url_root)
    base, ext = os.path.splitext(os.path.basename(file_name))
    basedir = os.path.dirname(file_name)
    for file in fnmatch.filter(os.listdir(basedir), _THUMBNAIL_GLOB % (base, ext)):
        path = os.path.join(basedir, file)
        os.remove(path)
        image_cache.delete(path) # delete from cache
#

def remove_model_thumbnails(model):
    """ remove all thumbnails for all ImageFields (and subclasses) in the model """
    
    for obj in model._meta.fields:
        if isinstance(obj, ImageField):
            url = getattr(model, 'get_%s_url' % obj.name)()
            _remove_thumbnails(url)
    #
#

def _make_admin_thumbnail(url):
    """ make thumbnails for admin interface """
    make_thumbnail(url, width=120)
#

def make_admin_thumbnails(model):
    """ create thumbnails for admin interface for all ImageFields (and subclasses) in the model """
    
    for obj in model._meta.fields:
        if isinstance(obj, ImageField):
            url = getattr(model, 'get_%s_url' % obj.name)()
            make_thumbnail(url, width=120)
    #
#

def _get_thumbnail_url(photo_url, width=None, height=None, root=MEDIA_ROOT, url_root=MEDIA_URL):
    """ return thumbnail URL for requested photo_url and required width and/or height
    
        if thumbnail file do not exists returns original URL
        (Does this ever get called?)
    """

    # one of width/height is required
    assert (width is not None) or (height is not None)
    
    if _has_thumbnail(photo_url, width, height, root, url_root):
        return _get_thumbnail_path(photo_url, width, height)
    else:
        return photo_url
#

def _no_pil_image_size(fname):
    """
        Determine the image type of FNAME and return its size.
        ripped from draco
        
        returns tuple (width, height) or None
    """
    
    try:
        filehandle = file(fname, 'rb')
    except IOError:
        return None

    head = filehandle.read(24)
    if len(head) != 24:
        return
    if head[:4] == '\x89PNG':
        # PNG
        check = struct.unpack('>i', head[4:8])[0]
        if check != 0x0d0a1a0a:
            return
        width, height = struct.unpack('>ii', head[16:24])
    elif head[:6] in ('GIF87a', 'GIF89a'):
        # GIF
        width, height = struct.unpack('<HH', head[6:10])
    elif head[:4] == '\xff\xd8\xff\xe0' and head[6:10] == 'JFIF':
        # JPEG
        filehandle.seek(0)  # Read 0xff next
        size = 2
        filetype = 0
        while not 0xc0 <= filetype <= 0xcf:
            filehandle.seek(size, 1)
            byte = filehandle.read(1)
            while ord(byte) == 0xff:
                byte = filehandle.read(1)
            filetype = ord(byte)
            size = struct.unpack('>H', filehandle.read(2))[0] - 2
        # We are at a SOFn block
        filehandle.seek(1, 1)  # Skip `precision' byte.
        height, width = struct.unpack('>HH', filehandle.read(4))
    else:
        return
    return width, height
#

def _set_cached_file(path, value):
    """ Store file dependent data in cache.
        Timeout is set to _FILE_CACHE_TIMEOUT (1month).
    """
    
    mtime = os.path.getmtime(path)
    image_cache.set(path, (mtime, value,), _FILE_CACHE_TIMEOUT)
#

def _get_cached_file(path, default=None):
    """ Get file content from cache.
        If modification time differ return None and delete
        data from cache.
    """
    
    cached = image_cache.get(path, default)
    if cached is None:
        return None
    mtime, value = cached
    
    if (not os.path.isfile(path)) or (os.path.getmtime(path) != mtime): # file is changed or deleted
        image_cache.delete(path) # delete from cache
        # remove thumbnails if exists
        base, ext = os.path.splitext(os.path.basename(path))
        basedir = os.path.dirname(path)
        for file in fnmatch.filter(os.listdir(basedir), _THUMBNAIL_GLOB % (base, ext)):
            os.remove(os.path.join(basedir, file))
        return None
    else:
        return value
#

def get_image_size(photo_url, root=MEDIA_ROOT, url_root=MEDIA_URL):
    """ returns image size, use PIL if present or _no_pil_image_size if no PIL is found.
    
        image sizes are cached (using separate locmem:/// cache instance)
    """
    
    path = os.path.join(root, _get_path_from_url(photo_url, root, url_root))
    
    size = _get_cached_file(path)
    if size is None:
        try:
            if HAS_PIL:
                size = Image.open(path).size
            else:
                size = _no_pil_image_size(path)
        except Exception, err:
            # this goes to webserver error log
            import sys
            print >>sys.stderr, '[GET IMAGE SIZE] error %s for file %r' % (err, photo_url)
            return None, None
        #
        if size is not None:
            _set_cached_file(path, size)
        else:
            return None, None
    #
    return size
#
