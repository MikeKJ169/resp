from django.forms import ModelForm
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from smartpages.models import SmartPage
from django.template import RequestContext
from contact.models import Type, Contact

class ContactForm(ModelForm):
    class Meta:
        model = Contact

def contact(request):
    if request.POST:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            type = form.cleaned_data['type']
            content = form.cleaned_data['content']
            msg_header = "Here is the content of the form.\n\n"
            msg_middle = "Name: %s\n\n" % name
            msg_middle += "Email address: %s\n\n" % email
            msg_middle += "Selected Type: %s\n\n" % type
            msg_middle += "Comments: %s\n\n" % content
            send_mail(settings.EMAIL_SUBJECT_PREFIX +"Email from your contact form", msg_header+msg_middle, settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_EMAIL_TO,], fail_silently=False)
            form.save()
            return HttpResponseRedirect("/thank-you/")
        else:
            form = ContactForm(request.POST)
    else:
        form = ContactForm()
    try:
        content = SmartPage.objects.get(slug='contact-us')
    except SmartPage.DoesNotExist:
        content = None
    return render_to_response("contact/form.html", {'form' : form, 'content' : content,}, context_instance=RequestContext(request))

