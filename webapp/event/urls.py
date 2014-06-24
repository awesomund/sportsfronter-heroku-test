from django.conf.urls import patterns, url

urlpatterns = patterns('event.views',
	url(r'^save', 'save_event', name='save_event'),
    url(r'^delete', 'delete_event', name='deleteevent'),
    url(r'^sendsingleinvitation', 'send_single_invitation', name='sendsingleinvitation'),
    url(r'^rsvpdata', 'rsvp_data', name='rsvpdata'),
    url(r'^rsvp/coach', 'rsvp_coach', name='rsvp_coach'),
    url(r'^rsvp', 'rsvp', name='rsvp'),
    url(r'^returnEventsPlayer', 'return_events_player'),
    url(r'^returnEventsCoach', 'return_events_coach'),
    url(r'^returnEventsGuardian', 'return_events_guardian'),
    url(r'^(?P<event_id>\d+)', 'get_event', name='getevent'),
)