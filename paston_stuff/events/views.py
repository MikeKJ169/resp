# Create your views here.
from events.models import Event
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from datetime import datetime, date
from django.template import RequestContext

def index(request):
    events = Event.objects.current()
    return render_to_response('events/index.html', {'events': events,}, context_instance=RequestContext(request))
    
def archive(request):
    events = Event.objects.archive()
    return render_to_response('events/index.html', {'events' : events}, context_instance=RequestContext(request))

def detail(request, events_id):
    n = get_object_or_404(Event,pk=events_id)
    if n.pub_date > datetime.now():
        raise Http404
    if n.expiry_date and (n.expiry_date < date.today()):
        raise Http404
    return render_to_response('events/event.html', {'event': n,}, context_instance=RequestContext(request))


def day(request, year, month, day):
    
    chosen_day_start = datetime(year=int(year), month=int(month), day=int(day), hour=0, minute=0)
    chosen_day_end = datetime(year=int(year), month=int(month), day=int(day)+1, hour=0, minute=0)
    events = Event.objects.filter( start_date__lte = chosen_day_end, end_date__gte = chosen_day_start )
    #raise NameError( event.attending )
    for event in events:
        event.user_is_attending = request.user in event.attending.all()
    return render_to_response('events/day.html', {'events': events}, context_instance=RequestContext(request))


def attend_event( request, event_id ):
    
    event = get_object_or_404( Event, pk=event_id )
    event.attending.add( request.user )
    event.save()

    return HttpResponseRedirect( "/events/" )

def unattend_event( request, event_id ):
    
    event = get_object_or_404( Event, pk=event_id )
    event.attending.remove( request.user )
    event.save()

    return HttpResponseRedirect( "/events/" )
