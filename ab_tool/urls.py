from django.conf.urls import patterns, url

from ab_tool.views.main_pages import (render_control_panel, not_authorized,
    tool_config, download_track_assignments, download_intervention_point_interactions)

from ab_tool.views.selection_pages import (resource_selection, submit_selection)
from ab_tool.views.intervention_point_pages import (submit_create_intervention_point,
    delete_intervention_point, deploy_intervention_point,
    submit_edit_intervention_point, modules_page_edit_intervention_point,
    modules_page_view_intervention_point,
    submit_edit_intervention_point_from_modules)
from ab_tool.views.experiment_pages import (create_experiment, submit_create_experiment,
    edit_experiment, submit_edit_experiment, delete_experiment, finalize_tracks,
    copy_experiment, delete_track, track_selection_xlsx, track_selection_csv,
    upload_track_assignments)

urlpatterns = patterns('',
    url(r'^$', render_control_panel, name='ab_testing_tool_index'),
    url(r'^not_authorized$', not_authorized, name='ab_testing_tool_not_authorized'),
    url(r'^download_track_assignments/(?P<experiment_id>\d+)$', download_track_assignments, name='ab_testing_tool_download_data'),
    url(r'^download_intervention_point_interactions/(?P<experiment_id>\d+)$', download_intervention_point_interactions,
        name='ab_testing_tool_download_intervention_point_interactions'),
    url(r'^tool_config$', tool_config, name='ab_testing_tool_tool_config'),
    
    url(r'^resource_selection$', resource_selection, name="ab_testing_tool_resource_selection"),
    url(r'^submit_selection$', submit_selection, name="ab_testing_tool_submit_selection"),
    # TODO: re-enable submit_selection_new_intervention_point() once it is available through the UI
    # url(r'^submit_selection_new_intervention_point$', submit_selection_new_intervention_point, name="ab_testing_tool_submit_selection_new_intervention_point"),
    
    url(r'^submit_create_intervention_point/(?P<experiment_id>\d+)$', submit_create_intervention_point, name='ab_testing_tool_submit_create_intervention_point'),
    url(r'^modules_page_view_intervention_point/(?P<intervention_point_id>\d+)$', modules_page_view_intervention_point, name='ab_testing_tool_modules_page_view_intervention_point'),
    url(r'^modules_page_edit_intervention_point/(?P<intervention_point_id>\d+)$', modules_page_edit_intervention_point, name='ab_testing_tool_modules_page_edit_intervention_point'),
    url(r'^submit_edit_intervention_point/(?P<intervention_point_id>\d+)$', submit_edit_intervention_point, name='ab_testing_tool_submit_edit_intervention_point'),
    url(r'^submit_edit_intervention_point_from_modules/(?P<intervention_point_id>\d+)$', submit_edit_intervention_point_from_modules, name='ab_testing_tool_submit_edit_intervention_point_from_modules'),
    url(r'^intervention_point/(?P<intervention_point_id>\d+)$', deploy_intervention_point, name='ab_testing_tool_deploy_intervention_point'),
    url(r'^delete_intervention_point/(?P<intervention_point_id>\d+)$', delete_intervention_point, name='ab_testing_tool_delete_intervention_point'),
    
    url(r'^create_experiment$', create_experiment, name='ab_testing_tool_create_experiment'),
    url(r'^submit_create_experiment$', submit_create_experiment, name='ab_testing_tool_submit_create_experiment'),
    url(r'^edit_experiment/(?P<experiment_id>\d+)$', edit_experiment, name='ab_testing_tool_edit_experiment'),
    url(r'^submit_edit_experiment/(?P<experiment_id>\d+)$', submit_edit_experiment, name='ab_testing_tool_submit_edit_experiment'),
    url(r'^delete_experiment/(?P<experiment_id>\d+)$', delete_experiment, name='ab_testing_tool_delete_experiment'),
    url(r'^delete_track/(?P<track_id>\d+)$', delete_track, name='ab_testing_tool_delete_track'),
    url(r'^finalize_tracks/(?P<experiment_id>\d+)$', finalize_tracks, name='ab_testing_tool_finalize_tracks'),
    url(r'^copy_experiment/(?P<experiment_id>\d+)$', copy_experiment, name='ab_testing_tool_copy_experiment'),
    url(r'^track_selection_xlsx/(?P<experiment_id>\d+)$', track_selection_xlsx, name='ab_testing_tool_track_selection_xlsx'),
    url(r'^track_selection_csv/(?P<experiment_id>\d+)$', track_selection_csv, name='ab_testing_tool_track_selection_csv'),
    url(r'^upload_track_assignments/(?P<experiment_id>\d+)$', upload_track_assignments, name='ab_testing_tool_upload_track_assignments'),
)
