from django.shortcuts import render_to_response, redirect, get_object_or_404
from django_auth_lti.decorators import lti_role_required
from django.core.urlresolvers import reverse

from ab_tool.constants import ADMINS
from ab_tool.models import (Track, CourseSettings, InterventionPoint,
    TrackProbabilityWeight)
from ab_tool.canvas import get_lti_param
from ab_tool.exceptions import (UNAUTHORIZED_ACCESS,
    COURSE_TRACKS_ALREADY_FINALIZED, NO_TRACKS_FOR_COURSE)
from django.http.response import HttpResponse
from ab_tool.controllers import (post_param, get_incomplete_intervention_points,
    get_missing_track_weights, format_weighting)


@lti_role_required(ADMINS)
def create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    return render_to_response("ab_tool/edit_track.html")


@lti_role_required(ADMINS)
def edit_track(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    is_finalized = CourseSettings.get_is_finalized(course_id)
    context = {"track": track,
               "is_finalized": is_finalized}
    return render_to_response("ab_tool/edit_track.html", context)


@lti_role_required(ADMINS)
def submit_create_track(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    Track.objects.create(name=name, notes=notes, course_id=course_id)
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def submit_edit_track(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    track.update(name=name, notes=notes)
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def delete_track(request, track_id):
    """
    NOTE: When a track gets deleted, urls for that track get deleted from all
          intervention_points in that course as a result of cascading delete.
    """
    track = get_object_or_404(Track, pk=track_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    if course_id != track.course_id:
        raise UNAUTHORIZED_ACCESS
    track.delete()
    return redirect(reverse("ab:index"))


@lti_role_required(ADMINS)
def finalize_tracks(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    tracks = Track.objects.filter(course_id=course_id)
    if tracks.count() == 0:
        raise NO_TRACKS_FOR_COURSE
    intervention_points = InterventionPoint.objects.filter(course_id=course_id)
    incomplete_intervention_points = get_incomplete_intervention_points(intervention_points)
    if incomplete_intervention_points:
        return HttpResponse("URLs missing for these tracks in these Intervention Points: %s" % incomplete_intervention_points)
    missing_track_weights = get_missing_track_weights(tracks, course_id)
    if missing_track_weights:
        return HttpResponse("Track weightings missing for these tracks: %s" % missing_track_weights)
    CourseSettings.set_finalized(course_id)
    return redirect(reverse("ab:index"))

@lti_role_required(ADMINS)
def track_weights(request):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    all_tracks = Track.objects.filter(course_id=course_id)
    weighting_objs = []
    for track in all_tracks:
        try:
            weighting_obj = TrackProbabilityWeight.objects.get(track=track)
            weighting_objs.append((track, weighting_obj))
        except TrackProbabilityWeight.DoesNotExist:
            weighting_objs.append((track, None))
    context = {"weighting_objs": weighting_objs,
               "cancel_url": reverse("ab:index") + "#tabs-5",
              }
    return render_to_response("ab_tool/edit_track_weights.html", context)

@lti_role_required(ADMINS)
def submit_track_weights(request):
    WEIGHT_TAG = "weight_for_track_"
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_ALREADY_FINALIZED
    intervention_pointurls = [(k,v) for (k,v) in request.POST.iteritems() if WEIGHT_TAG in k and v]
    for (k,v) in intervention_pointurls:
        _, track_id = k.split(WEIGHT_TAG)
        try:
            intervention_point_url = TrackProbabilityWeight.objects.get(track__pk=track_id)
            intervention_point_url.update(weighting=format_weighting(v))
        except TrackProbabilityWeight.DoesNotExist:
            TrackProbabilityWeight.objects.create(weighting=format_weighting(v),  track_id=track_id)
    return redirect(reverse("ab:index") + "#tabs-5")

