from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^lti_tools/ab_testing/', include('ab_testing_tool_app.urls', namespace="ab")),
)
