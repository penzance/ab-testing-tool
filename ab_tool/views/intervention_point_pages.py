from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django_auth_lti.decorators import lti_role_required

from ab_tool.constants import (ADMINS, STAGE_URL_TAG,
    DEPLOY_OPTION_TAG, AS_TAB_TAG)
from ab_tool.models import (InterventionPoint, Track, InterventionPointUrl,
     ExperimentStudent, Experiment)
from ab_tool.canvas import get_lti_param, CanvasModules
from ab_tool.controllers import (format_url, post_param, assign_track_and_create_student)
from ab_tool.exceptions import (DELETING_INSTALLED_STAGE,
    EXPERIMENT_TRACKS_NOT_FINALIZED, NO_URL_FOR_TRACK)
from ab_tool.analytics import log_intervention_point_interaction


def deploy_intervention_point(request, intervention_point_id):
    """
    Delivers randomly one of the urls in intervention_point if user is not an admin,
    or edit_intervention_point panel if admin.
    Note: Do not put @lti_role_required(ADMINS) here, as students can reach
    this page.
    TODO: Have admin able to preview intervention_points as a student would see them
    """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    # TODO: replace the following code with verification.is_allowed
    # when that code makes it into django_auth_lti master
    user_roles = get_lti_param(request, "roles")
    
    # If user is an admin, let them edit the intervention_point
    if set(ADMINS) & set(user_roles):
        return redirect(reverse("ab_testing_tool_modules_page_edit_intervention_point",
                                args=(intervention_point_id,)))
    
    intervention_point = InterventionPoint.get_or_404_check_course(
            intervention_point_id, course_id)
    
    experiment = intervention_point.experiment
    
    # Otherwise, user is a student.  Tracks for the course must be finalized
    # for a student to be able to access content from the ab_testing_tool
    if not experiment.tracks_finalized:
        raise EXPERIMENT_TRACKS_NOT_FINALIZED
    
    student_id = get_lti_param(request, "custom_canvas_user_login_id")
    
    # Get or create an object to track the student for this course
    try:
        student = ExperimentStudent.objects.get(student_id=student_id, experiment=experiment)
    except ExperimentStudent.DoesNotExist:
        # If this is a new student or the student doesn't yet have a track,
        # select a track before creating the student. This avoids a race condition of
        # a student existing but not having a track assigned (e.g. if the update to
        # a student database object fails)
        lis_person_sourcedid = get_lti_param(request, "lis_person_sourcedid")
        student = assign_track_and_create_student(experiment, student_id, lis_person_sourcedid)
    
    # Retrieve the url for the student's track at the current intervention point
    # Return an error page if there is no url configured.
    try:
        chosen_intervention_point_url = InterventionPointUrl.objects.get(intervention_point__pk=intervention_point_id, track=student.track)
    except InterventionPointUrl.DoesNotExist:
        raise NO_URL_FOR_TRACK
    if not chosen_intervention_point_url.url:
        raise NO_URL_FOR_TRACK
    
    log_intervention_point_interaction(course_id, student, intervention_point, experiment)
    
    if chosen_intervention_point_url.open_as_tab:
        return render_to_response("ab_tool/new_tab_redirect.html", {"url": chosen_intervention_point_url.url})
    if chosen_intervention_point_url.is_canvas_page:
        return render_to_response("ab_tool/window_redirect.html", {"url": chosen_intervention_point_url.url})
    return redirect(chosen_intervention_point_url.url)


@lti_role_required(ADMINS)
def submit_create_intervention_point(request, experiment_id):
    """ Note: request will always be POST because Canvas fetches pages within iframe by POST
        TODO: use Django forms library to save instead of getting individual POST params """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    experiment = Experiment.get_or_404_check_course(experiment_id, course_id)
    intervention_point = InterventionPoint.objects.create(
            name=name, notes=notes, course_id=course_id, experiment=experiment)
    intervention_pointurls = [(k,v) for (k,v) in request.POST.iteritems()
                              if STAGE_URL_TAG in k and v]
    for (k,v) in intervention_pointurls:
        _, track_id = k.split(STAGE_URL_TAG)
        is_canvas = post_param(request, DEPLOY_OPTION_TAG + track_id)
        as_tab = request.POST.get(AS_TAB_TAG + track_id, None)
        is_canvas_page = bool(is_canvas == "canvas_url")
        open_as_tab = bool(as_tab == "true")
        InterventionPointUrl.objects.create(
                url=format_url(v), intervention_point_id=intervention_point.id,
                track_id=track_id, is_canvas_page=is_canvas_page, open_as_tab=open_as_tab
        )
    return redirect(reverse("ab_testing_tool_index"))


@lti_role_required(ADMINS)
def modules_page_edit_intervention_point(request, intervention_point_id):
    context = edit_intervention_point_common(request, intervention_point_id)
    return render_to_response("ab_tool/modules_page_edit_intervention_point.html", context)


def edit_intervention_point_common(request, intervention_point_id):
    """ Common core shared between edit_intervention_point and modules_page_edit_intervention_point """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    canvas_modules = CanvasModules(request)
    intervention_point = InterventionPoint.get_or_404_check_course(
            intervention_point_id, course_id)
    all_tracks = Track.objects.filter(course_id=course_id,
                                      experiment=intervention_point.experiment)
    track_urls = []
    for track in all_tracks:
        # This is a search for the joint unique index of InterventionPointUrl, so it
        # should not ever return multiple objects
        try:
            intervention_point_url = InterventionPointUrl.objects.get(intervention_point__pk=intervention_point_id, track=track)
            track_urls.append((track, intervention_point_url))
        except InterventionPointUrl.DoesNotExist:
            track_urls.append((track, None))
    context = {"intervention_point": intervention_point,
               "tracks": track_urls,
               "is_installed": canvas_modules.intervention_point_is_installed(intervention_point),
               #TODO: "installed_module": installed_module,
               }
    return context


@lti_role_required(ADMINS)
def submit_edit_intervention_point(request, intervention_point_id):
    """ Note: Only allowed if admin has privileges on the particular course.
        TODO: consider using Django forms to save rather of getting individual POST params """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    intervention_point = InterventionPoint.get_or_404_check_course(
            intervention_point_id, course_id)
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    intervention_point.update(name=name, notes=notes)
    # InterventionPointUrl creation
    intervention_pointurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in intervention_pointurls:
        _, track_id = k.split(STAGE_URL_TAG)
        # This is a search for the joint unique index of InterventionPointUrl, so it
        # should not ever return multiple objects
        deploy_option = post_param(request, DEPLOY_OPTION_TAG + track_id)
        is_canvas_page = bool(deploy_option == "canvasPage")
        open_as_tab = bool(deploy_option == "newTab")
        try:
            intervention_point_url = InterventionPointUrl.objects.get(intervention_point__pk=intervention_point_id, track__pk=track_id)
            intervention_point_url.update(url=format_url(v), is_canvas_page=is_canvas_page, open_as_tab=open_as_tab)
        except InterventionPointUrl.DoesNotExist:
            InterventionPointUrl.objects.create(url=format_url(v), intervention_point_id=intervention_point_id, track_id=track_id,
                                    is_canvas_page=is_canvas_page, open_as_tab=open_as_tab)
    return redirect(reverse("ab_testing_tool_index"))


@lti_role_required(ADMINS)
def delete_intervention_point(request, intervention_point_id):
    """ Note: Installed intervention_points are not allowed to be deleted
        Note: attached InterventionPointUrls are deleted via cascading delete """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    intervention_point = InterventionPoint.get_or_404_check_course(
            intervention_point_id, course_id)
    canvas_modules = CanvasModules(request)
    if canvas_modules.intervention_point_is_installed(intervention_point):
        raise DELETING_INSTALLED_STAGE
    intervention_point.delete()
    return redirect(reverse("ab_testing_tool_index"))
