def get_list_of_child_categories_and_objects(app_label, model_name, cat_slug=None, cat_id=None):
    from django.db.models.loading import get_model

    Model=get_model(app_label,model_name)
    Category=get_model(app_label,'Category')

    if cat_slug:
        try:
            cat=Category.objects.get(slug=cat_slug)
        except Category.DoesNotExist:
            return []
    elif cat_id:
        try:
            cat = Category.objects.get(pk=cat_id)
        except Category.DoesNotExist:
            return []
    else:
        raise AttributeError("get_list_of_child_categories_and_objects got nothing to work on (no cat_slug, no cat_id)")



    mylist=[]
#        for c in cat.child_set.all():
    for c in Category.objects.filter(parent=cat.id):
        mylist.append({'id':c.id, 'priority':c.priority, 'url':c.get_absolute_url(), 'name':c.name, 'childtype':'Category','object':c})
    
    if model_name != 'Category':
#       for p in cat.smartpage_set.all():
        # There *must* be a nicer way to do this:
        for p in getattr(cat,model_name.lower()+'_set').all():
            mylist.append({'id':p.id, 'priority':p.priority, 'url':p.get_absolute_url(), 'name':p.name, 'childtype':model_name, 'object':p})
    
    mylist.sort(lambda f, s: cmp(f['priority'], s['priority']))

    return mylist
