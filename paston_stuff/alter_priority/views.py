from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

def alter_priority(request, content_type_id, object_id, up_or_down):
    content_type = ContentType.objects.get(id=content_type_id)
    model = content_type.model_class()
    if not request.user.has_perm(content_type.app_label + '.' + model._meta.get_change_permission()):
        return PermissionDenied
    obj = model.objects.get(id=object_id)
    object_list = model.objects.order_by('priority')
    if up_or_down == 'up':
#abortive attempt at more intelligent movement:
#        for i, object in enumerate(object_list):
#            if object.id == obj.id:
#                obj_index = i
#                break
#        print obj_index
#
#        if obj_index > 0:
#            if obj.priority > object_list[obj_index-1].priority:
#                # set new priority to same as previous object
#                # (so they're sorted by the next ordering)
#                old_obj_priority = obj.priority
#                obj.priority = object_list[obj_index-1].priority
#                object_list[obj_index-1].priority = old_obj_priority
#            else:
#                obj.priority = object_list[obj_index-1].priority-1
         


        obj.priority = obj.priority-1
        obj.save()
    elif up_or_down == 'down':
        obj.priority = obj.priority+1
        obj.save()
    return HttpResponseRedirect('/admin/%s/%s/' % (content_type.app_label, model._meta.object_name.lower()))

def priority_controls_func(self):
    """ not actually a view, this is a method for putting in
        putting in your model class to get up / down buttons """
    content_type = ContentType.objects.get_for_model(self)
    return '<a href="/alter-priority/up/%d/%d/">Up</a>  <a href="/alter-priority/down/%d/%d/">Down</a>' % (content_type.id, self.id, content_type.id, self.id)
priority_controls_func.allow_tags=True
