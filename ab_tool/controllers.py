from django.core.urlresolvers import reverse
from random import choice

from ab_tool.models import (TrackProbabilityWeight, Experiment, ExperimentStudent)
from ab_tool.exceptions import (BAD_STAGE_ID, missing_param_error,
    INPUT_NOT_ALLOWED, NO_TRACKS_FOR_EXPERIMENT, TRACK_WEIGHTS_NOT_SET,
    CSV_UPLOAD_NEEDED)


def assign_track_and_create_student(experiment, student_id, lis_person_sourcedid):
    """ Method looks up assignment_mode to select track and creates student in selected track.
        Method returns student object """
    if experiment.assignment_method == Experiment.CSV_UPLOAD:
        # Raise error as student should have already been assigned a track if CSV upload
        #TODO: infrastructure needed notify course administrator about incomplete student-track mapping
        raise CSV_UPLOAD_NEEDED
    tracks = experiment.tracks.all()
    if not tracks:
        raise NO_TRACKS_FOR_EXPERIMENT
    if experiment.assignment_method == Experiment.UNIFORM_RANDOM:
        # If uniform, pick randomly from the set of tracks
        chosen_track = choice(tracks)
    if experiment.assignment_method == Experiment.WEIGHTED_PROBABILITY_RANDOM:
        # If weighted, generate a weighted list of tracks and pick one randomly from list
        weighted_tracks = []
        for track in tracks:
            try:
                track_weight = TrackProbabilityWeight.objects.get(track=track, experiment=experiment)
            except TrackProbabilityWeight.DoesNotExist:
                raise TRACK_WEIGHTS_NOT_SET
            weighted_tracks.extend([track] * track_weight.weighting)
        chosen_track = choice(weighted_tracks)
    # Create student with chosen track
    student = ExperimentStudent.objects.create(
            student_id=student_id, course_id=experiment.course_id,
            track=chosen_track, lis_person_sourcedid=lis_person_sourcedid,
            experiment=experiment
    )
    return student


def intervention_point_url(request, intervention_point_id):
    """ Builds a URL to deploy the intervention_point with the database id
        intervention_point_id """
    try:
        intervention_point_id = int(intervention_point_id)
    except (TypeError, ValueError):
        raise BAD_STAGE_ID
    return request.build_absolute_uri(reverse("ab:deploy_intervention_point",
                                              args=(intervention_point_id,)))

def format_url(url):
    """ Adds "http://" to the beginning of a url if it isn't there """
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "http://%s" % url


def get_incomplete_intervention_points(intervention_point_list):
    """ Takes paramter intervention_point_list instead of parameter course_id to avoid
        second database call to the InterventionPoint table in methods that needs to
        already fetch the InterventionPoint table"""
    return [intervention_point.name for intervention_point in intervention_point_list
            if intervention_point.is_missing_urls()]


def get_missing_track_weights(experiment, course_id):
    if experiment.assignment_method != Experiment.WEIGHTED_PROBABILITY_RANDOM:
        return []
    missing_weights = []
    track_weights = [t.track for t in
                     TrackProbabilityWeight.objects.filter(course_id=course_id, experiment=experiment)]
    for track in experiment.tracks.all():
        if track not in track_weights:
            missing_weights.append(track)
    return [track.name for track in missing_weights]


def format_weighting(weighting):
    """ Track weights need to be an integer between 1 and 1000, allowing
        probability precision up to 0.001 """
    weighting = int(weighting)
    if 1 <= weighting <= 1000:
        return weighting
    else:
        raise INPUT_NOT_ALLOWED

def post_param(request, param_name):
    if param_name in request.POST:
        return request.POST[param_name]
    raise missing_param_error(param_name)
