from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^lti_tools/ab_tool/', include("ab_testing_tool_app.urls", namespace="ab", app_name="ab_tool")),
)
