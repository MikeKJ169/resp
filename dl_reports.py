from django.shortcuts import render_to_response
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.db import connection
from django import forms
from django.forms import ModelForm
import csv
from django.db.models.loading import get_model
from django.template.defaultfilters import slugify
from contact.models import Type, Contact
from django.contrib.auth.models import User


class ContactReportForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContactReportForm, self).__init__(*args, **kwargs)
    my_model = forms.ModelChoiceField(queryset=Type.objects.all())
    
    class Meta:
        model = Type

@staff_member_required
@never_cache
def contact_report(request, fields=None):
    form = ContactReportForm()
    type = ''
    if request.GET:
        form = ContactReportForm(request.GET)
        if form.is_valid():
            if form.cleaned_data.has_key('type'):
                selected_type = form.cleaned_data['type']
                qs = Contact.objects.filter(type=type)
            else:
                qs = Contact.objects.all()
            model = qs.model
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
            writer = csv.writer(response)
            # Write headers to CSV file
            if fields:
                headers = fields
            else:
                headers = []
                for field in model._meta.fields:
                    headers.append(field.name)
            writer.writerow(headers)
            # Write data to CSV file
            for obj in qs:
                row = []
                for field in headers:
                    if field in headers:
                        val = getattr(obj, field)
                        if callable(val):
                            val = val()
                        row.append(val)
                writer.writerow(row)
            # Return CSV file to browser as download
            return response
        else:
            pass
    set = Contact.objects.all()
    return render_to_response('admin/contact_report.html', {'form': form,'set': set, }, context_instance = RequestContext(request))
 
