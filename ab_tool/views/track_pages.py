from django.shortcuts import render_to_response, redirect
from django_auth_lti.decorators import lti_role_required
from django.core.urlresolvers import reverse

from ab_tool.constants import ADMINS
from ab_tool.models import (Track, Experiment, TrackProbabilityWeight)
from ab_tool.canvas import get_lti_param
from ab_tool.exceptions import (NO_TRACKS_FOR_EXPERIMENT)
from django.http.response import HttpResponse
from ab_tool.controllers import (post_param, get_missing_track_weights,
    format_weighting, get_incomplete_intervention_points)


@lti_role_required(ADMINS)
def create_experiment(request):
    context = {"Experiment": Experiment}
    return render_to_response("ab_tool/edit_experiment.html", context)


@lti_role_required(ADMINS)
def submit_create_experiment(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    assignment_method = int(post_param(request, "assignment_method"))
    if assignment_method == Experiment.UNIFORM_RANDOM:
        num_tracks = int(post_param(request, "uniform_tracks"))
    if assignment_method == Experiment.WEIGHTED_PROBABILITY_RANDOM:
        track_weights = request.POST.getlist(request, "track_weights[]")
        num_tracks = len(track_weights)
    experiment = Experiment.objects.create(name=name, course_id=course_id,
                                           assignment_method=assignment_method,
                                           notes=notes)
    experiment.set_number_of_tracks(num_tracks)
    if assignment_method == Experiment.WEIGHTED_PROBABILITY_RANDOM:
        experiment.set_track_weights(track_weights)
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def edit_experiment(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    all_tracks = Track.objects.filter(course_id=course_id, experiment=experiment)
    track_weights = []
    for track in all_tracks:
        try:
            weight = TrackProbabilityWeight.objects.get(experiment=experiment,track=track).weighting
            track_weights.append((track, weight))
        except TrackProbabilityWeight.DoesNotExist:
            track_weights.append((track, None))
    context = {"Experiment": Experiment,
               "experiment": experiment,
               "tracks": track_weights,
               }
    return render_to_response("ab_tool/edit_experiment.html", context)


@lti_role_required(ADMINS)
def submit_edit_experiment(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    assignment_method = int(post_param(request, "assignment_method"))
    if assignment_method == Experiment.UNIFORM_RANDOM:
        num_tracks = int(post_param(request, "uniform_tracks"))
    if assignment_method == Experiment.WEIGHTED_PROBABILITY_RANDOM:
        track_weights = request.POST.getlist(request, "track_weights[]")
        num_tracks = len(track_weights)
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    experiment.update(name=name, course_id=course_id,
                      assignment_method=assignment_method, notes=notes)
    experiment.set_number_of_tracks(num_tracks)
    if assignment_method == Experiment.WEIGHTED_PROBABILITY_RANDOM:
        experiment.set_track_weights(track_weights)
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def delete_experiment(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    experiment.assert_not_finalized()
    experiment.delete()
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def submit_edit_track(request, track_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    track = Track.get_or_404_check_course(track_id, course_id)
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    track.update(name=name, notes=notes)
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def delete_track(request, track_id):
    #TODO: delete
    """
    NOTE: When a track gets deleted, urls for that track get deleted from all
          intervention_points in that course as a result of cascading delete.
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    track = Track.get_or_404_check_course(track_id, course_id)
    track.experiment.assert_not_finalized()
    track.delete()
    return redirect(reverse("ab:index"))


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
    missing_track_weights = get_missing_track_weights(experiment.tracks.all(), course_id)
    if missing_track_weights:
        return HttpResponse("Track weightings missing for these tracks: %s" % missing_track_weights)
    experiment.tracks_finalized = True
    experiment.save()
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def submit_track_weights(request, experiment_id):
    #TODO: delete
    WEIGHT_TAG = "weight_for_track_"
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    experiment.assert_not_finalized()
    weightings = [(k,v) for (k,v) in request.POST.iteritems() if WEIGHT_TAG in k and v]
    for (k,v) in weightings:
        _, track_id = k.split(WEIGHT_TAG)
        try:
            weighting_obj = TrackProbabilityWeight.objects.get(
                    track__pk=track_id, experiment=experiment)
            weighting_obj.update(weighting=format_weighting(v))
        except TrackProbabilityWeight.DoesNotExist:
            TrackProbabilityWeight.objects.create(
                track_id=track_id, course_id=course_id, experiment=experiment,
                weighting=format_weighting(v)
            )
    return redirect(reverse("ab:index") + "#tabs-5")
