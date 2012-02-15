from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^login/$', 'django_haikus.views.login', name="trainer-login"),
    url(r'^logout/$', 'django_haikus.views.logout', name="trainer-logout"),
    url(r'^/(?P<id>\d+)/(?P<rating>\d+)/', 'django_haikus.views.train', name="set-rating"),
    url(r'^/(?P<id>\d+)/(?P<tag>\w+)/', 'django_haikus.views.train', name="add-tag"),
    url(r'^$', 'django_haikus.views.train', name="train"),
)
