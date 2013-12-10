from django.db import models
from django import oldforms as forms
from django.utils.html import escape
from django.conf import settings

def unique_slug(model, name, excluded_ids = []):
    # Turn the name into a slug and make ensure it's unique:
    from django.template.defaultfilters import slugify

    slug = slugify(name)
    dupes=model.objects.filter(slug=slug).exclude(id__in = excluded_ids)

    if dupes.count()==0:
        return slug
    else:
        i=2
        while True:
            dupes=model.objects.filter(slug='%s-%d' % (slug,i)).exclude(id__in = excluded_ids)
            if dupes.count() == 0: break
            i+=1

        return '%s-%s' % (slug,str(i))




def get_object_or_none(klass, *args, **kwargs):
    try:
        return klass._default_manager.get(*args, **kwargs)
    except klass.DoesNotExist:
        pass


class BadFunctionCall(Exception):
    "Function called with inappropriate arguments"
    pass

def get_list_of_child_categories_and_objects(app_label, model_name, cat_slug=None, cat_id=None):
    from django.db.models.loading import get_model

    Model=get_model(app_label,model_name)
    Category=get_model(app_label,'Category')

    if cat_slug:
        try:
            cat=Category.objects.get(slug=cat_slug)
        except Category.DoesNotExist:
            return
    elif cat_id:
        try:
            cat = Category.objects.get(pk=cat_id)
        except Category.DoesNotExist:
            return
    else:
        raise BadFunctionCall


    mylist=[]
#        for c in cat.child_set.all():
    for c in Category.objects.filter(parent=cat.id):
        mylist.append({'id':c.id, 'priority':c.priority, 'url':c.get_absolute_url(), 'name':c.name, 'childtype':'Category',})
    
    if model_name != 'Category':
#       for p in cat.smartpage_set.all():
        # There *must* be a nicer way to do this:
        for p in getattr(cat,model_name.lower()+'_set').all():
            mylist.append({'id':p.id, 'priority':p.priority, 'url':p.get_absolute_url(), 'name':p.name, 'childtype':model_name,})
    
    mylist.sort(lambda f, s: cmp(f['priority'], s['priority']))

    return mylist
    

class SmartPageTextFieldManipulator(forms.LargeTextField):
    def render(self,data):
        if isinstance(data, unicode):
            data = data.encode(settings.DEFAULT_CHARSET)
        if not data:
            data = '<p></p>'
        else:
            data = escape(data)
        return '<textarea id="%s" class="v%s%s " name="%s" rows="%s" cols="%s">%s</textarea>' % \
            (self.get_id(), 'SmartPageTextField', self.is_required and ' required' or '',
            self.field_name, self.rows, self.cols, data)

class SmartPageTextField(models.TextField):
    def get_manipulator_field_objs(self):
        return [SmartPageTextFieldManipulator]

    def get_internal_type(self):
        return "TextField"

class HtmlFieldManipulator(forms.LargeTextField):
    def render(self,data):
        if isinstance(data, unicode):
            data = data.encode(settings.DEFAULT_CHARSET)
        if not data:
            data = '<p></p>'
        else:
            data = escape(data)
        return '<textarea id="%s" class="v%s%s " name="%s" rows="%s" cols="%s">%s</textarea>' % \
            (self.get_id(), 'HtmlField', self.is_required and ' required' or '',
            self.field_name, self.rows, self.cols, data)

class HtmlField(models.TextField):
    def get_manipulator_field_objs(self):
        return [HtmlFieldManipulator]

    def get_internal_type(self):
        return "TextField"

import re, datetime
from django import oldforms as forms
from django.core import validators

def calculate_age(dob):
    """
    Pass in dob as datetime.date object or else
    ... it won't work
    """
#    if not type(dob) == datetime.date:
#        pass
    today = datetime.date.today()

    years = today.year - dob.year
    if dob.month > today.month:
        years = years - 1
    months = today.month - dob.month

    if months < 0:
        months = 12 - months

    if dob.day > today.day:
        if months > 0:
            months = months - 1
        else:
           months = 11
           years = years - 1
        if today.month > 1:
            days = (datetime.date(today.year, today.month, today.day) - datetime.date(today.year, today.month - 1, dob.day)).days
        else:
            days = (datetime.date(today.year, today.month, today.day) - datetime.date(today.year - 1, 12, dob.day)).days
    else:
        days = today.day - dob.day
    return (days, months, years)

class UKDateField(forms.FormField):
    def UKDateValidator(field_data, all_data):
        # split on . or / and expect to get three items
        fields = re.split(r'[\./]', field_data)
        if len(fields) != 3:
            raise validators.ValidationError("Date must look like: 30/10/2006")
        try:
            fields = map(int, fields)
        except ValueError:
            raise validators.ValidationError("Only use numerical date parts.")
        if fields[2] < 1900:
            raise validators.ValidationError("Incorrect date format.")
        try:
            d = datetime.date(fields[2], fields[1], fields[0])
        except ValueError:
            raise validators.ValidationError("Invalid date")

        return True
    UKDateValidator = staticmethod(UKDateValidator)

    def html2python(data):
        # data is allready validated
        fields = map(int, re.split(r'[\./]', data))
        return datetime.date(fields[2], fields[1], fields[0])
    html2python = staticmethod(html2python)

    def __init__(self, field_name='', is_required=False, validator_list=None):
        if validator_list is None: validator_list = []
        self.is_required = is_required
        self.validator_list = [self.UKDateValidator] + validator_list
        self.field_name = field_name
        self.is_required = is_required
   
    def render(self, data):
        widget = '<input id="%s" name="%s" type="text" value="%s" />'
        return widget % (self.get_id(), self.field_name, forms.escape(data))
