from django.conf.urls import patterns, url, include
from django.contrib import admin

from ab_testing_tool_app.views.main_pages import (render_stage_control_panel, not_authorized,
     tool_config, download_data)

from ab_testing_tool_app.views.selection_pages import (resource_selection, submit_selection,
                    submit_selection_new_stage)
from ab_testing_tool_app.views.stage_pages import (create_stage, submit_create_stage,
                    edit_stage,  delete_stage, deploy_stage, submit_edit_stage)
from ab_testing_tool_app.views.track_pages import (create_track, submit_create_track,
                    submit_edit_track, edit_track, delete_track, finalize_tracks)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', render_stage_control_panel, name='index'),
    url(r'^not_authorized$', not_authorized, name='not_authorized'),
    url(r'^download_data$', download_data, name='download_data'),
    url(r'^tool_config$', tool_config, name='tool_config'),
    url(r'^resource_selection$', resource_selection, name="resource_selection"),
    url(r'^submit_selection$', submit_selection, name="submit_selection"),
    url(r'^submit_selection_new_stage', submit_selection_new_stage, name="submit_selection_new_stage"),
    
    url(r'^create_stage$', create_stage, name='create_stage'),
    url(r'^submit_create_stage$', submit_create_stage, name='submit_create_stage'),
    url(r'^edit_stage/(?P<stage_id>\d+)$', edit_stage, name='edit_stage'),
    url(r'^submit_edit_stage$', submit_edit_stage, name='submit_edit_stage'),
    url(r'^stage/(?P<stage_id>\d+)$', deploy_stage, name='deploy_stage'),
    url(r'^delete_stage/(?P<stage_id>\d+)$', delete_stage, name='delete_stage'),
    
    url(r'^create_track', create_track, name='create_track'),
    url(r'^submit_create_track$', submit_create_track, name='submit_create_track'),
    url(r'^edit_track/(?P<track_id>\d+)$', edit_track, name='edit_track'),
    url(r'^submit_edit_track$', submit_edit_track, name='submit_edit_track'),
    url(r'^delete_track/(?P<track_id>\d+)$', delete_track, name='delete_track'),
    url(r'^finalize_tracks$', finalize_tracks, name='finalize_tracks'),
    
    url(r'^admin/', include(admin.site.urls)),
)
