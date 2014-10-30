from django.conf.urls import patterns, url

from ab_tool.views.main_pages import (render_intervention_point_control_panel, not_authorized,
     tool_config, download_data)

from ab_tool.views.selection_pages import (resource_selection, submit_selection,
    submit_selection_new_intervention_point)
from ab_tool.views.intervention_point_pages import (create_intervention_point,
    submit_create_intervention_point, edit_intervention_point,
    delete_intervention_point, deploy_intervention_point,
    submit_edit_intervention_point, modules_page_edit_intervention_point)
from ab_tool.views.track_pages import (create_experiment, submit_create_experiment,
    edit_experiment, submit_edit_experiment, delete_experiment, finalize_tracks)

urlpatterns = patterns('',
    url(r'^$', render_intervention_point_control_panel, name='index'),
    url(r'^not_authorized$', not_authorized, name='not_authorized'),
    url(r'^download_data$', download_data, name='download_data'),
    url(r'^tool_config$', tool_config, name='tool_config'),
    url(r'^resource_selection$', resource_selection, name="resource_selection"),
    url(r'^submit_selection$', submit_selection, name="submit_selection"),
    url(r'^submit_selection_new_intervention_point$', submit_selection_new_intervention_point, name="submit_selection_new_intervention_point"),
    
    url(r'^create_intervention_point$', create_intervention_point, name='create_intervention_point'),
    url(r'^submit_create_intervention_point/(?P<experiment_id>\d+)$', submit_create_intervention_point, name='submit_create_intervention_point'),
    url(r'^edit_intervention_point/(?P<intervention_point_id>\d+)$', edit_intervention_point, name='edit_intervention_point'),
    url(r'^modules_page_edit_intervention_point/(?P<intervention_point_id>\d+)$', modules_page_edit_intervention_point, name='modules_page_edit_intervention_point'),
    url(r'^submit_edit_intervention_point/(?P<intervention_point_id>\d+)$', submit_edit_intervention_point, name='submit_edit_intervention_point'),
    url(r'^intervention_point/(?P<intervention_point_id>\d+)$', deploy_intervention_point, name='deploy_intervention_point'),
    url(r'^delete_intervention_point/(?P<intervention_point_id>\d+)$', delete_intervention_point, name='delete_intervention_point'),
    
    url(r'^finalize_tracks/(?P<experiment_id>\d+)$', finalize_tracks, name='finalize_tracks'),

    url(r'^create_experiment$', create_experiment, name='create_experiment'),
    url(r'^submit_create_experiment$', submit_create_experiment, name='submit_create_experiment'),
    url(r'^edit_experiment/(?P<experiment_id>\d+)$', edit_experiment, name='edit_experiment'),
    url(r'^submit_edit_experiment/(?P<experiment_id>\d+)$', submit_edit_experiment, name='submit_edit_experiment'),
    url(r'^delete_experiment/(?P<experiment_id>\d+)$', delete_experiment, name='delete_experiment'),
)
