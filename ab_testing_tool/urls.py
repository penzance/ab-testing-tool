from django.conf.urls import patterns, include, url
from django.contrib import admin

from ab_tool.views.main_pages import not_authorized

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^not_authorized$', not_authorized, name='not_authorized'),
    url(r'^lti_tools/ab_tool/', include("ab_tool.urls", namespace="ab", app_name="ab_tool")),

    url(r'^admin/', include(admin.site.urls)),
)
