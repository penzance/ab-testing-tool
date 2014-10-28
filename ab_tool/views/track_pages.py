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
    return render_to_response("ab_tool/edit_experiment.html")


@lti_role_required(ADMINS)
def submit_create_experiment(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    num_tracks = post_param(request, "num_tracks")
    experiment = Experiment.objects.create(name=name, course_id=course_id)
    for i in range(num_tracks):
        Track.objects.create(name="Track %s" % i, course_id=course_id,
                             experiment=experiment)
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def view_experiment(request, experiment_id):
    pass


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
def track_weights(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_placeholder_course_experiment(course_id)
    experiment.assert_not_finalized()
    weighting_objs = []
    for track in experiment.tracks.all():
        try:
            weighting_obj = TrackProbabilityWeight.objects.get(
                    track=track, experiment=experiment)
            weighting_objs.append((track, weighting_obj))
        except TrackProbabilityWeight.DoesNotExist:
            weighting_objs.append((track, None))
    context = {"weighting_objs": weighting_objs,
               "cancel_url": reverse("ab:index") + "#tabs-5",
               "experiment_id": experiment.id,
              }
    return render_to_response("ab_tool/edit_track_weights.html", context)


@lti_role_required(ADMINS)
def submit_track_weights(request, experiment_id):
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
