from django.conf.urls import patterns, include, url
from django.contrib import admin

from ab_testing_tool.views import (render_stage_control_panel, not_authorized,
    deploy_stage, submit_edit_stage, tool_config, resource_selection,
    submit_selection, create_stage, submit_create_stage, edit_stage, create_track,
    submit_create_track, submit_edit_track, edit_track, delete_track, delete_stage,
    submit_selection_new_stage)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', render_stage_control_panel, name='index'),
    url(r'^not_authorized$', not_authorized, name='not_authorized'),
    url(r'^tool_config$', tool_config, name='tool_config'),
    url(r'^resource_selection$', resource_selection, name="resource_selection"),
    url(r'^submit_selection$', submit_selection, name="submit_selection"),
    url(r'^submit_selection_new_stage', submit_selection_new_stage, name="submit_selection_new_stage"),

    url(r'^create_stage$', create_stage, name='create_stage'),
    url(r'^submit_create_stage$', submit_create_stage, name='submit_create_stage'),
    url(r'^edit_stage/(?P<t_id>\d+)$', edit_stage, name='edit_stage'),
    url(r'^submit_edit_stage$', submit_edit_stage, name='submit_edit_stage'),
    url(r'^stage/(?P<t_id>\d+)$', deploy_stage, name='render_stage'),
    url(r'^delete_stage/(?P<t_id>\d+)$', delete_stage, name='delete_stage'),

    url(r'^create_track', create_track, name='create_track'),
    url(r'^submit_create_track$', submit_create_track, name='submit_create_track'),
    url(r'^edit_track/(?P<track_id>\d+)$', edit_track, name='edit_track'),
    url(r'^submit_edit_track$', submit_edit_track, name='submit_edit_track'),
    url(r'^delete_track/(?P<track_id>\d+)$', delete_track, name='delete_track'),

    # Examples:
    # url(r'^$', 'project_name.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^admin/', include(admin.site.urls)),
)
