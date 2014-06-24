from django.conf.urls import patterns, url

urlpatterns = patterns('auth.views',
	url(r'^login', '_login'),
	url(r'^register', 'register'),
    url(r'^logout', 'logout_view'),
    url(r'^isauth', 'is_auth'),
    url(r'^send_user_info', 'send_user_info'),
    url(r'^get_user_roles', 'get_user_roles'),
)