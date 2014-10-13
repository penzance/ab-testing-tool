from django.shortcuts import render_to_response, redirect
from django_auth_lti.decorators import lti_role_required
from django.core.urlresolvers import reverse

from ab_tool.constants import ADMINS
from ab_tool.models import Track, Experiment
from ab_tool.canvas import get_lti_param
from ab_tool.exceptions import (NO_TRACKS_FOR_EXPERIMENT,
    EXPERIMENT_TRACKS_ALREADY_FINALIZED)
from django.http.response import HttpResponse
from ab_tool.controllers import (post_param, get_incomplete_intervention_points)


@lti_role_required(ADMINS)
def create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_placeholder_course_experiment(course_id)
    if experiment.tracks_finalized:
        raise EXPERIMENT_TRACKS_ALREADY_FINALIZED
    return render_to_response("ab_tool/edit_track.html", {"experiment_id": experiment.id})


@lti_role_required(ADMINS)
def edit_track(request, track_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    track = Track.get_or_404_check_course(track_id, course_id)
    is_finalized = track.experiment.tracks_finalized
    context = {"track": track,
               "is_finalized": is_finalized}
    return render_to_response("ab_tool/edit_track.html", context)


@lti_role_required(ADMINS)
def submit_create_track(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    if experiment.tracks_finalized:
        raise EXPERIMENT_TRACKS_ALREADY_FINALIZED
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    Track.objects.create(name=name, notes=notes, course_id=course_id,
                         experiment=experiment)
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
    """
    NOTE: When a track gets deleted, urls for that track get deleted from all
          intervention_points in that course as a result of cascading delete.
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    track = Track.get_or_404_check_course(track_id, course_id)
    if track.experiment.tracks_finalized:
        raise EXPERIMENT_TRACKS_ALREADY_FINALIZED
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
        #TODO: replace with better error display
        return HttpResponse("URLs missing for these tracks in these Intervention Points: %s"
                            % incomplete_intervention_points)
    experiment.tracks_finalized = True
    experiment.save()
    return redirect(reverse("ab:index"))
