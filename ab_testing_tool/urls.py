from django.conf.urls import patterns, include, url
from django.contrib import admin

from ab_testing_tool.views import (render_treatment_control_panel, not_authorized,
    deploy_treatment, update_treatment, get_treatment, tool_config, lti_launch,
    submit_selection)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', render_treatment_control_panel, name='index'),
    url(r'^not_authorized$', not_authorized, name='not_authorized'),
    url(r'^lti_launch$', lti_launch, name="lti_launch"),
    url(r'^submit_selection$', submit_selection, name="submit_selection"),
    url(r'^tool_config$', tool_config, name='tool_config'),
    
    url(r'^update_treatment$', update_treatment, name='update_treatment'),
    url(r'^edit_treatment/$', get_treatment, name='edit_treatment'),
    url(r'^edit_treatment/(?P<t_id>\d+)$', get_treatment, name='edit_treatment'),
    url(r'^treatment/(?P<t_id>\d+)$', deploy_treatment, name='render_treatment'),
    url(r'^(?P<unique_id>\d+)/(?P<t_id>\d+)$', deploy_treatment, name='render_treatment'),
    
    # Examples:
    # url(r'^$', 'project_name.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^admin/', include(admin.site.urls)),
)
