    from django.conf.urls import patterns, url, include
from django.contrib import admin

from ab_testing_tool_app.views.main_pages import (render_intervention_point_control_panel, not_authorized,
     tool_config, download_data)

from ab_testing_tool_app.views.selection_pages import (resource_selection, submit_selection,
                    submit_selection_new_intervention_point)
from ab_testing_tool_app.views.intervention_point_pages import (create_intervention_point, submit_create_intervention_point,
                    edit_intervention_point,  delete_intervention_point, deploy_intervention_point, submit_edit_intervention_point,
                    modules_page_edit_intervention_point)
from ab_testing_tool_app.views.track_pages import (create_track, submit_create_track,
                    submit_edit_track, edit_track, delete_track, finalize_tracks)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', render_intervention_point_control_panel, name='index'),
    url(r'^not_authorized$', not_authorized, name='not_authorized'),
    url(r'^download_data$', download_data, name='download_data'),
    url(r'^tool_config$', tool_config, name='tool_config'),
    url(r'^resource_selection$', resource_selection, name="resource_selection"),
    url(r'^submit_selection$', submit_selection, name="submit_selection"),
    url(r'^submit_selection_new_intervention_point', submit_selection_new_intervention_point, name="submit_selection_new_intervention_point"),
    
    url(r'^create_intervention_point$', create_intervention_point, name='create_intervention_point'),
    url(r'^submit_create_intervention_point$', submit_create_intervention_point, name='submit_create_intervention_point'),
    url(r'^edit_intervention_point/(?P<intervention_point_id>\d+)$', edit_intervention_point, name='edit_intervention_point'),
    url(r'^modules_page_edit_intervention_point/(?P<intervention_point_id>\d+)$', modules_page_edit_intervention_point, name='modules_page_edit_intervention_point'),
    url(r'^submit_edit_intervention_point/(?P<intervention_point_id>\d+)$', submit_edit_intervention_point, name='submit_edit_intervention_point'),
    url(r'^intervention_point/(?P<intervention_point_id>\d+)$', deploy_intervention_point, name='deploy_intervention_point'),
    url(r'^delete_intervention_point/(?P<intervention_point_id>\d+)$', delete_intervention_point, name='delete_intervention_point'),
    
    url(r'^create_track', create_track, name='create_track'),
    url(r'^submit_create_track$', submit_create_track, name='submit_create_track'),
    url(r'^edit_track/(?P<track_id>\d+)$', edit_track, name='edit_track'),
    url(r'^submit_edit_track/(?P<track_id>\d+)$', submit_edit_track, name='submit_edit_track'),
    url(r'^delete_track/(?P<track_id>\d+)$', delete_track, name='delete_track'),
    url(r'^finalize_tracks$', finalize_tracks, name='finalize_tracks'),
    
    url(r'^admin/', include(admin.site.urls)),
)
