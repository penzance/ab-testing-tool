from django.conf.urls import patterns, url, include
from oauth import oauth_callback

urlpatterns = patterns('',
    url(r'^canvas_redirect$', oauth_callback, name='oauth_page'),
)
