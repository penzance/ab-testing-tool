from django.conf.urls import patterns, include, url

from django.contrib import admin
from ab_testing_tool.views import index, not_authorized, tool_config, lti_launch
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', index, name="index"),
    url(r'^not_authorized$', not_authorized, name='not_authorized'),
    url(r'^lti_launch$', lti_launch, name="lti_launch"),
    url(r'^tool_config$', tool_config, name='tool_config'),
    
    # Examples:
    # url(r'^$', 'project_name.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
)
