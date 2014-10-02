from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^lti_tools/ab_tool/', include("ab_tool.urls", namespace="ab", app_name="ab_tool")),
)
