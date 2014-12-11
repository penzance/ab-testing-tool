import json
from django.shortcuts import render_to_response, redirect
from django_auth_lti.decorators import lti_role_required
from django.core.urlresolvers import reverse

from ab_tool.constants import ADMINS
from ab_tool.models import (Track, Experiment, TrackProbabilityWeight,
    InterventionPoint, InterventionPointUrl)
from ab_tool.canvas import get_lti_param, CanvasModules
from ab_tool.exceptions import (NO_TRACKS_FOR_EXPERIMENT,
    INTERVENTION_POINTS_ARE_INSTALLED)
from django.http.response import HttpResponse
from ab_tool.controllers import (post_param, get_missing_track_weights,
    get_incomplete_intervention_points)


@lti_role_required(ADMINS)
def create_experiment(request):
    context = {"create": True}
    return render_to_response("ab_tool/editExperiment.html", context)


@lti_role_required(ADMINS)
def submit_create_experiment(request):
    """ Expects a post parameter 'experiment' to be json of the form:
            {"name": name(str),
             "notes": notes(str),
             "uniformRandom": True/False,
             "tracks": [{"id": None # This is none for all because all tracks are new
                         "weighting": track_weighting(int),
                         "name": track_name(str),
                        }]
            }
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment_dict = json.loads(request.body)
    
    # Unpack data from experiment_dict and update experiment
    name = experiment_dict["name"]
    notes = experiment_dict["notes"]
    uniform_random = experiment_dict["uniformRandom"]
    tracks = experiment_dict["tracks"]
    if uniform_random:
        assignment_method = Experiment.UNIFORM_RANDOM
    else:
        assignment_method = Experiment.WEIGHTED_PROBABILITY_RANDOM
    experiment = Experiment.objects.create(
            name=name, course_id=course_id, notes=notes,
            assignment_method=assignment_method
    )
    
    # Update existing tracks
    for track_dict in tracks:
        track = experiment.new_track(track_dict["name"])
        if not uniform_random:
            track.set_weighting(track_dict["weighting"])
    return redirect(reverse("ab_testing_tool_index"))


@lti_role_required(ADMINS)
def edit_experiment(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    has_installed_intervention = CanvasModules(request).experiment_has_installed_intervention(experiment)
    context = {"experiment": experiment,
               "experiment_has_installed_intervention": has_installed_intervention,
               "create": False,}
    return render_to_response("ab_tool/editExperiment.html", context)


@lti_role_required(ADMINS)
def delete_track(request, track_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    track = Track.get_or_404_check_course(track_id, course_id)
    track.delete()
    return HttpResponse("success")


@lti_role_required(ADMINS)
def submit_edit_experiment(request, experiment_id):
    """ Expects a post parameter 'experiment' to be json of the form:
            {"name": name(str),
             "notes": notes(str),
             "uniformRandom": True/False,
             "tracks": [{"id": track_id(int), # this is None if track is new
                         "weighting": track_weighting(int),
                         "name": track_name(str),
                        }]
            }
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    experiment.assert_not_finalized()
    experiment_dict = json.loads(request.body)
    
    # Unpack data from experiment_dict and update experiment
    name = experiment_dict["name"]
    notes = experiment_dict["notes"]
    uniform_random = experiment_dict["uniformRandom"]
    old_tracks = [i for i in experiment_dict["tracks"] if i["id"] is not None]
    new_tracks = [i for i in experiment_dict["tracks"] if i["id"] is None]
    if uniform_random:
        assignment_method = Experiment.UNIFORM_RANDOM
    else:
        assignment_method = Experiment.WEIGHTED_PROBABILITY_RANDOM
    experiment.update(name=name, notes=notes, assignment_method=assignment_method)
    
    # Update existing tracks
    for track_dict in old_tracks:
        track = Track.get_or_404_check_course(track_dict["id"], course_id)
        track.update(name=track_dict["name"])
        if not uniform_random:
            track.set_weighting(track_dict["weighting"])
    
    # Create new tracks
    for track_dict in new_tracks:
        track = experiment.new_track(track_dict["name"])
        if not uniform_random:
            track.set_weighting(track_dict["weighting"])
    return redirect(reverse("ab_testing_tool_index"))

@lti_role_required(ADMINS)
def copy_experiment(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    orig_exp = Experiment.get_or_404_check_course(experiment_id, course_id)
    copied_name = "%s_copy" % orig_exp.name
    copied_name = "%s%s" % (copied_name, len(Experiment.objects.filter(course_id=course_id,
                                                                       name=copied_name)) + 1)
    # Copies Experiment
    copied_exp = Experiment.objects.create(
            name=copied_name, course_id=course_id, notes=orig_exp.notes,
            assignment_method=orig_exp.assignment_method
    )
    track_id_mapping = {}
    # Copies Tracks
    for orig_track in orig_exp.tracks.all():
        track_id_mapping[orig_track.id] = Track.objects.create(name=orig_track.name, experiment=copied_exp)
    # Copies TrackProbabilityWeights, if any
    for orig_weight in orig_exp.track_probabilites.all():
        TrackProbabilityWeight.objects.create(weighting=orig_weight.weighting,
                                              name=orig_weight.name,
                                              experiment=copied_exp)
    # Copies InterventionPoints,
    for orig_ip in orig_exp.intervention_points.all():
        copied_ip = InterventionPoint.objects.create(name=orig_ip.name,
                                         notes=orig_ip.notes,
                                         experiment=copied_exp)
        # Copies InterventionPointUrls, if any
        for orig_ip_url in InterventionPointUrl.objects.filter(intervention_point=copied_ip):
            InterventionPointUrl.objects.create(url=orig_ip_url.url,
                                                intervention_point=copied_ip,
                                                track=track_id_mapping[orig_ip_url.track.id],
                                                open_as_tab=orig_ip_url.open_as_tab,
                                                is_canvas_page=orig_ip_url.is_canvas_page)
    return redirect(reverse("ab_testing_tool_index"))


@lti_role_required(ADMINS)
def delete_experiment(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    experiment.assert_not_finalized()
    canvas_modules = CanvasModules(request)
    if canvas_modules.experiment_has_installed_intervention(experiment):
        raise INTERVENTION_POINTS_ARE_INSTALLED
    experiment.delete()
    return redirect(reverse("ab_testing_tool_index"))


@lti_role_required(ADMINS)
def finalize_tracks(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    if not experiment.tracks.count():
        raise NO_TRACKS_FOR_EXPERIMENT
    intervention_points = experiment.intervention_points.all()
    incomplete_intervention_points = get_incomplete_intervention_points(intervention_points)
    if incomplete_intervention_points:
        return HttpResponse("URLs missing for these tracks in these Intervention Points: %s"
                            % incomplete_intervention_points)
    missing_track_weights = get_missing_track_weights(experiment, course_id)
    if missing_track_weights:
        return HttpResponse("Track weightings missing for these tracks: %s" % missing_track_weights)
    experiment.tracks_finalized = True
    experiment.save()
    return redirect(reverse("ab_testing_tool_index"))
