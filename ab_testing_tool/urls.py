from django.conf.urls import patterns, include, url
from django.contrib import admin

from ab_tool.views.main_pages import not_authorized

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^not_authorized$', not_authorized, name='not_authorized'),
    url(r'^lti/', include("ab_tool.urls", app_name="ab_tool")),
    url(r'^oauth/', include("django_canvas_oauth.urls", namespace="django_canvas_oauth")),
    url(r'^admin/', include(admin.site.urls)),
)
