from django.conf.urls import patterns, include, url
from socialneo.views import HomeView, ProfileView, SubmitView, MyProfileView, NEOListView, NEOItemView, NEOItemObserveView

from django.contrib.auth.views import logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^profile/?$', MyProfileView.as_view(), name='my_profile'),
    url(r'^profile/(?P<user>.+)?$', ProfileView.as_view(), name='my_profile'),

    url(r'^submit/?$', SubmitView.as_view(), name='submit'),
    # url(r'^project/', include('project.foo.urls')),

    url(r'^logout/?$', logout, {'next_page': '/'}, name='socialauth_logout'),
    url(r'', include('social_auth.urls')),

    url(r'^neo/?$', NEOListView.as_view(), name='neo_list'),
    url(r'^neo/(?P<neo_id>\d+)$', NEOItemView.as_view(), name='neo_item'),
    url(r'^neo/(?P<neo_id>\d+)/observe/?$', NEOItemObserveView.as_view(), name='neo_item_observe'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
