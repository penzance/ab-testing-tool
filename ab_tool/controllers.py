from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from random import choice

from ab_tool.models import (InterventionPoint, TrackProbabilityWeight,
    CourseSettings, Track, CourseStudent)
from ab_tool.canvas import (get_canvas_request_context, list_module_items, list_modules,
    get_lti_param)
from ab_tool.exceptions import (BAD_STAGE_ID, missing_param_error,
    INPUT_NOT_ALLOWED)

from ab_tool.exceptions import (NO_TRACKS_FOR_COURSE, TRACK_WEIGHTS_NOT_SET,
    CSV_UPLOAD_NEEDED)


def assign_track_and_create_student(course_id, student_id, lis_person_sourcedid):
    """ Method looks up assignment_mode to select track and creates student in selected track.
        Method returns student object """
    course_settings = get_object_or_404(CourseSettings, course_id=course_id)
    if course_settings.assignment_method == CourseSettings.CSV_UPLOAD:
        # Raise error as student should have already been assigned a track if CSV upload
        #TODO: infrastructure needed notify course administrator about incomplete student-track mapping
        raise CSV_UPLOAD_NEEDED
    tracks = Track.objects.filter(course_id=course_id)
    if not tracks:
        raise NO_TRACKS_FOR_COURSE
    if course_settings.assignment_method == CourseSettings.UNIFORM_RANDOM:
        # If uniform, pick randomly from the set of tracks
        chosen_track = choice(tracks)
    if course_settings.assignment_method == CourseSettings.WEIGHTED_PROBABILITY_RANDOM:
        # If weighted, generate a weighted list of tracks appropriately and pick one randomly from list
        weighted_tracks = []
        for track in tracks:
            try:
                track_weight = TrackProbabilityWeight.objects.get(track=track, course_id=course_id)
            except TrackProbabilityWeight.DoesNotExist:
                raise TRACK_WEIGHTS_NOT_SET
            weighted_tracks.extend([track] * track_weight.weighting)
        chosen_track = choice(weighted_tracks)
    # Create student with chosen track
    student = CourseStudent.objects.create(
            student_id=student_id, course_id=course_id, track=chosen_track,
            lis_person_sourcedid=lis_person_sourcedid)
    return student


def intervention_point_url(request, intervention_point_id):
    """ Builds a URL to deploy the intervention_point with the database id intervention_point_id """
    try:
        intervention_point_id = int(intervention_point_id)
    except (TypeError, ValueError):
        raise BAD_STAGE_ID
    return request.build_absolute_uri(reverse("ab:deploy_intervention_point", args=(intervention_point_id,)))


def format_url(url):
    """ Adds "http://" to the beginning of a url if it isn't there """
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "http://%s" % url


def get_uninstalled_intervention_points(request):
    """ Returns the list of InterventionPoint objects that have been created for the
        current course but not installed in any of that course's modules """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    installed_intervention_point_urls = get_installed_intervention_points(request)
    intervention_points = [intervention_point for intervention_point in InterventionPoint.objects.filter(course_id=course_id)
              if intervention_point_url(request, intervention_point.id) not in installed_intervention_point_urls]
    return intervention_points


def get_installed_intervention_points(request):
    """ Returns the list of InterventionPointUrls (as strings) for InterventionPoints that have been
        installed in at least one of the courses modules. """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context =  get_canvas_request_context(request)
    all_modules = list_modules(request_context, course_id)
    installed_intervention_point_urls = []
    for module in all_modules:
        module_items = list_module_items(request_context, course_id, module["id"])
        intervention_point_urls = [item["external_url"] for item in module_items
                      if item["type"] == "ExternalTool"]
        installed_intervention_point_urls.extend(intervention_point_urls)
    return installed_intervention_point_urls

def intervention_point_is_installed(request, intervention_point):
    return intervention_point_url(request, intervention_point.id) in get_installed_intervention_points(request)

def get_incomplete_intervention_points(intervention_point_list):
    """ Takes paramter intervention_point_list instead of parameter course_id to avoid
        second database call to the InterventionPoint table in methods that needs to
        already fetch the InterventionPoint table"""
    return [intervention_point.name for intervention_point in intervention_point_list if intervention_point.is_missing_urls()]

def all_intervention_point_urls(request, course_id):
    """ Returns the deploy urls of all intervention_points in the database for that course"""
    return [intervention_point_url(request, intervention_point.id) for intervention_point in
            InterventionPoint.objects.filter(course_id=course_id)]

def get_missing_track_weights(tracks, course_id):
    course_settings,_ = CourseSettings.objects.get_or_create(course_id=course_id)
    if course_settings.assignment_method != CourseSettings.WEIGHTED_PROBABILITY_RANDOM:
        return []
    missing_weights = []
    track_weights = [t.track for t in TrackProbabilityWeight.objects.filter(course_id=course_id)]
    for track in tracks:
        if track not in track_weights:
            missing_weights.append(track)
    return [track.name for track in missing_weights]

def format_weighting(weighting):
    """ Track weights need to be an integer between 1 and 1000, allowing
        probability precision up to 0.001 """
    if 1 <= int(weighting) <= 1000:
        return int(weighting)
    else:
        print weighting
        raise INPUT_NOT_ALLOWED


def get_modules_with_items(request):
    """
    Returns a list of all modules with the items of that module added to the
    module under the extra attribute "module_items" (this is a list).
    Each item in those lists has the added attribute "is_intervention_point", which is a
    boolean describing whether or not the item is a intervention_point of the ab_testing_tool
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    request_context = get_canvas_request_context(request)
    intervention_point_urls = all_intervention_point_urls(request, course_id)
    modules = list_modules(request_context, course_id)
    for module in modules:
        module["module_items"] = list_module_items(request_context, course_id,
                                                   module["id"])
        for item in module["module_items"]:
            is_intervention_point = (item["type"] == "ExternalTool" and "external_url" in item
                        and item["external_url"] in intervention_point_urls)
            item["is_intervention_point"] = is_intervention_point
    return modules


def post_param(request, param_name):
    if param_name in request.POST:
        return request.POST[param_name]
    raise missing_param_error(param_name)
