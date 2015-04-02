import json
from django.shortcuts import render_to_response, redirect, render
from django.views.decorators.http import require_POST
from django_auth_lti.decorators import lti_role_required
from django.core.urlresolvers import reverse
from django.conf import settings

from ab_tool.constants import ADMINS
from ab_tool.models import (Track, Experiment, ExperimentStudent)
from ab_tool.canvas import get_lti_param, CanvasModules, get_unassigned_students
from ab_tool.exceptions import (NO_TRACKS_FOR_EXPERIMENT,
    INTERVENTION_POINTS_ARE_INSTALLED, FILE_TOO_LARGE, COPIES_EXCEEDS_LIMIT)
from django.http.response import HttpResponse, Http404

from ab_tool.controllers import (get_missing_track_weights,
    get_incomplete_intervention_points, validate_weighting, validate_name)
from ab_tool.spreadsheets import (get_track_selection_xlsx, get_track_selection_csv,
    parse_uploaded_file)


@lti_role_required(ADMINS)
def create_experiment(request):
    context = {"create": True, "started": False}
    return render(request, "ab_tool/edit_experiment.html", context)


@lti_role_required(ADMINS)
def submit_create_experiment(request):
    """ Expects a post parameter 'experiment' to be json of the form:
            {"name": name(str),
             "notes": notes(str),
             "uniformRandom": True/False,
             "csvUpload": True/False,
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
    csv_upload = bool(experiment_dict["csvUpload"])

    # Validates using backend rules before any object creation
    for track_dict in tracks:
        validate_name(track_dict["name"])
        # added check for csv upload. if we are uploading a csv file
        # we don't want track weights
        if not uniform_random and not csv_upload:
            validate_weighting(track_dict["weighting"])

    if csv_upload:
        assignment_method = Experiment.CSV_UPLOAD
    elif uniform_random:
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
        if not uniform_random and not csv_upload:
            track.set_weighting(track_dict["weighting"])
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
    return render(request, "ab_tool/edit_experiment.html", context)


# TODO: CSRF protection e.g. implement as POST
@lti_role_required(ADMINS)
def delete_track(request, track_id):
    """ If Http404 is raised, delete_track redirects regardless. This is by
        design, as multiple users may be deleting concurrently in the same course """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    try:
        track = Track.get_or_404_check_course(track_id, course_id)
        track.delete()
    except Http404:
        pass
    return HttpResponse("success")

@lti_role_required(ADMINS)
def submit_edit_experiment(request, experiment_id):
    """ Expects a post parameter 'experiment' to be json of the form:
            {"name": name(str),
             "notes": notes(str),
             "uniformRandom": True/False,
             "csvUpload": True/False,
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
    
    uniform_random = experiment_dict["uniformRandom"]
    csv_upload = experiment_dict["csvUpload"]
    existing_tracks = [i for i in experiment_dict["tracks"] if i["id"] is not None]
    new_tracks = [i for i in experiment_dict["tracks"] if i["id"] is None]
    if csv_upload:
        assignment_method = Experiment.CSV_UPLOAD
    elif uniform_random:
        assignment_method = Experiment.UNIFORM_RANDOM
    else:
        assignment_method = Experiment.WEIGHTED_PROBABILITY_RANDOM
    experiment.update(name=name, notes=notes, assignment_method=assignment_method)
    
    # Update existing tracks
    for track_dict in existing_tracks:
        track = Track.get_or_404_check_course(track_dict["id"], course_id)
        track.update(name=validate_name(track_dict["name"]))
        if not uniform_random and not csv_upload:
            track.set_weighting(validate_weighting(track_dict["weighting"]))
    
    # Create new tracks
    for track_dict in new_tracks:
        track = experiment.new_track(validate_name(track_dict["name"]))
        if not uniform_random and not csv_upload:
            track.set_weighting(validate_weighting(track_dict["weighting"]))
    return HttpResponse("success")


@require_POST
@lti_role_required(ADMINS)
def copy_experiment(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    experiments_with_prefix = set([e.name for e in Experiment.objects.filter(
            course_id=course_id, name__startswith=experiment.name)])
    for i in range(1,1000):
        new_name = "%s_copy%s" % (experiment.name, i)
        if new_name not in experiments_with_prefix:
            experiment.copy(new_name)
            return redirect(reverse("ab_testing_tool_index"))
    raise COPIES_EXCEEDS_LIMIT


@require_POST
@lti_role_required(ADMINS)
def delete_experiment(request, experiment_id):
    """ If Http404 is raised, delete_experiment redirects regardless. This is by
        design, as multiple users may be deleting concurrently in the same course """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    try:
        experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
        experiment.assert_not_finalized()
        canvas_modules = CanvasModules(request)
        if canvas_modules.experiment_has_installed_intervention(experiment):
            raise INTERVENTION_POINTS_ARE_INSTALLED
        experiment.delete()
    except Http404:
        pass
    return redirect(reverse("ab_testing_tool_index"))


# TODO: CSRF protection e.g. implement as POST
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


@lti_role_required(ADMINS)
def track_selection_xlsx(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    return get_track_selection_xlsx(request, experiment, "track_selection.xlsx")

@lti_role_required(ADMINS)
def track_selection_csv(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    return get_track_selection_csv(request, experiment, "track_selection.csv")

@lti_role_required(ADMINS)
def upload_track_assignments(request, experiment_id):
    course_id = get_lti_param(request, "custom_canvas_course_id")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    uploaded_file = request.FILES["track_assignments"]
    if (uploaded_file.size > int(settings.MAX_FILE_UPLOAD_SIZE)):
        raise FILE_TOO_LARGE
    uploaded_text = uploaded_file.read()
    unassigned_students = get_unassigned_students(request, experiment)
    students, errors = parse_uploaded_file(
            experiment, unassigned_students, uploaded_text, uploaded_file.name
    )
    if errors:
        return render_to_response("ab_tool/spreadsheetErrors.html", {"errors": errors})
    
    for student_id, track in students.items():
        # lis_person_sourcedid is not returned by SDK, so we set it to None
        ExperimentStudent.objects.create(
            student_id=student_id, course_id=experiment.course_id,
            track=track, student_name=unassigned_students[student_id],
            experiment=experiment
        )
    if not experiment.tracks_finalized:
        experiment.update(tracks_finalized=True)
    return redirect(reverse("ab_testing_tool_index"))
