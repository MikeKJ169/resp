from ring3.contact.views import ContactForm
from django import template

register = template.Library()

def show_form():
    form = ContactForm()
    return {'form' : form}
register.inclusion_tag('contact/form.html')(show_form)
