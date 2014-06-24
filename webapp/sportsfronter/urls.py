from settings import DOMAIN

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import Site

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

#Init stuff
site = Site.objects.get(pk=1)
site.domain = DOMAIN
site.name = "Sportsfronter"
site.save()

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sportsfronter.views.home', name='home'),
    # url(r'^sportsfronter/', include('sportsfronter.foo.urls')),
    url(r'^$', TemplateView.as_view(template_name='webapp/index.html'), name='index'),
    url(r'^index_ios.html$', TemplateView.as_view(template_name='webapp/index_ios.html'), name='ios'),
    url(r'^index_cordova.html$', TemplateView.as_view(template_name='webapp/index_cordova.html'), name='cordova'),

    # Password stuff:
    url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='admin_password_reset'),
    (r'^admin/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),

    url(r'^password/change/$', auth_views.password_change, name='auth_password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done, name='auth_password_change_done'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^event/', include('event.urls')),
    url(r'^auth/', include('auth.urls')),
    url(r'^management/', include('management.urls')),
    url(r'^push/', include('push.urls')),


    #url(r'^invite/(?P<email_hash>\S+)/$', 'push.views.invite'),
)
urlpatterns += url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'sportsfronter/static'}),


