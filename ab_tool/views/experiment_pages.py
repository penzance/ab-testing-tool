import json
from django.shortcuts import render_to_response, redirect
from django_auth_lti.decorators import lti_role_required
from django.core.urlresolvers import reverse

from ab_tool.constants import ADMINS
from ab_tool.models import Track, Experiment
from ab_tool.canvas import get_lti_param, CanvasModules
from ab_tool.exceptions import (NO_TRACKS_FOR_EXPERIMENT,
    INTERVENTION_POINTS_ARE_INSTALLED)
from django.http.response import HttpResponse
from ab_tool.controllers import (get_missing_track_weights,
    get_incomplete_intervention_points, validate_weighting, validate_name)


@lti_role_required(ADMINS)
def create_experiment(request):
    context = {"create": True, "started": False}
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
    name = validate_name(experiment_dict["name"])
    notes = experiment_dict["notes"]
    uniform_random = bool(experiment_dict["uniformRandom"])
    tracks = experiment_dict["tracks"]
    # Validates using backend rules before any object creation
    for track_dict in tracks:
        validate_name(track_dict["name"])
        if not uniform_random:
            validate_weighting(track_dict["weighting"])
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
        track = experiment.new_track(validate_name(track_dict["name"]))
        if not uniform_random:
            track.set_weighting(validate_weighting(track_dict["weighting"]))
    return HttpResponse("success")


@lti_role_required(ADMINS)
def edit_experiment(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    has_installed_intervention = CanvasModules(request).experiment_has_installed_intervention(experiment)
    context = {"experiment": experiment,
               "experiment_has_installed_intervention": has_installed_intervention,
               "create": False,
               "started": experiment.tracks_finalized}
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
    experiment_dict = json.loads(request.body)
    
    # Unpack data from experiment_dict and update experiment
    name = validate_name(experiment_dict["name"])
    notes = experiment_dict["notes"]
    if experiment.tracks_finalized:
        # Only allow updating name, notes, and track names for started experiments
        experiment.update(name=name, notes=notes)
        existing_tracks = [i for i in experiment_dict["tracks"] if i["id"] is not None]
        for track_dict in existing_tracks:
            track = Track.get_or_404_check_course(track_dict["id"], course_id)
            track.update(name=validate_name(track_dict["name"]))
        return HttpResponse("success")
    
    uniform_random = bool(experiment_dict["uniformRandom"])
    existing_tracks = [i for i in experiment_dict["tracks"] if i["id"] is not None]
    new_tracks = [i for i in experiment_dict["tracks"] if i["id"] is None]
    if uniform_random:
        assignment_method = Experiment.UNIFORM_RANDOM
    else:
        assignment_method = Experiment.WEIGHTED_PROBABILITY_RANDOM
    experiment.update(name=name, notes=notes, assignment_method=assignment_method)
    
    # Update existing tracks
    for track_dict in existing_tracks:
        track = Track.get_or_404_check_course(track_dict["id"], course_id)
        track.update(name=validate_name(track_dict["name"]))
        if not uniform_random:
            track.set_weighting(validate_weighting(track_dict["weighting"]))
    
    # Create new tracks
    for track_dict in new_tracks:
        track = experiment.new_track(validate_name(track_dict["name"]))
        if not uniform_random:
            track.set_weighting(validate_weighting(track_dict["weighting"]))
    return HttpResponse("success")


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
                            % ", ".join(incomplete_intervention_points))
    missing_track_weights = get_missing_track_weights(experiment, course_id)
    if missing_track_weights:
        return HttpResponse("Track weightings missing for these tracks: %s"
                            % ", ".join(missing_track_weights))
    experiment.tracks_finalized = True
    experiment.save()
    return redirect(reverse("ab_testing_tool_index"))
