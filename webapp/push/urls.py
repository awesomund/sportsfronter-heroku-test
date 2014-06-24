from django.conf.urls import patterns, url

urlpatterns = patterns('push.views',
	#url(r'^createEventPush', 'create_event_push'),
	url(r'^count_notifications', 'count_notifications')
)