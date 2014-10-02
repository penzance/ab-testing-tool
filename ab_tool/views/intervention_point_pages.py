from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django_auth_lti.decorators import lti_role_required
from random import choice

from ab_tool.constants import (ADMINS, STAGE_URL_TAG,
    DEPLOY_OPTION_TAG, AS_TAB_TAG)
from ab_tool.models import (InterventionPoint, Track, InterventionPointUrl, CourseSettings,
    CourseStudent)
from ab_tool.canvas import get_lti_param
from ab_tool.controllers import (intervention_point_is_installed, format_url,
    post_param)
from ab_tool.exceptions import (UNAUTHORIZED_ACCESS,
    DELETING_INSTALLED_STAGE, COURSE_TRACKS_NOT_FINALIZED,
    NO_URL_FOR_TRACK, NO_TRACKS_FOR_COURSE)


def deploy_intervention_point(request, intervention_point_id):
    """Delivers randomly one of the urls in intervention_point if user is not an admin, or
       edit_intervention_point panel if admin.
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
        return redirect(reverse("ab:modules_page_edit_intervention_point", args=(intervention_point_id,)))
    
    # Otherwise, user is a student.  Tracks for the course must be finalized
    # for a student to be able to access content from the ab_testing_tool
    if not CourseSettings.get_is_finalized(course_id):
        raise COURSE_TRACKS_NOT_FINALIZED
    
    student_id = get_lti_param(request, "custom_canvas_user_login_id")
    lis_person_sourcedid = get_lti_param(request, "lis_person_sourcedid")
    
    # Get or create an object to track the student for this course
    try:
        student = CourseStudent.objects.get(student_id=student_id, course_id=course_id)
    except CourseStudent.DoesNotExist:
        # If this is a new student or the student doesn't yet have a track,
        # assign the student to a track
        # TODO: expand this code to allow multiple randomization procedures
        tracks = Track.objects.filter(course_id=course_id)
        if not tracks:
            raise NO_TRACKS_FOR_COURSE
        chosen_track = choice(tracks)
        student = CourseStudent.objects.create(
                student_id=student_id, course_id=course_id, track=chosen_track,
                lis_person_sourcedid=lis_person_sourcedid)
    
    # Retrieve the url for the student's track at the current intervention point
    # Return an error page if there is no url configured.
    try:
        chosen_intervention_point_url = InterventionPointUrl.objects.get(intervention_point__pk=intervention_point_id, track=student.track)
        if chosen_intervention_point_url.open_as_tab:
            return render_to_response("ab_tool/new_tab_redirect.html", {"url": chosen_intervention_point_url.url})
        if chosen_intervention_point_url.is_canvas_page:
            return render_to_response("ab_tool/window_redirect.html", {"url": chosen_intervention_point_url.url})
    except InterventionPointUrl.DoesNotExist:
        raise NO_URL_FOR_TRACK
    if not chosen_intervention_point_url.url:
        raise NO_URL_FOR_TRACK
    return redirect(chosen_intervention_point_url.url)


@lti_role_required(ADMINS)
def create_intervention_point(request):
    """ Note: Canvas fetches all pages within iframe with POST request,
        requiring separate template render function. This also breaks CSRF
        token validation if CSRF Middleware is turned off. """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    #Note: Refer to template. (t,None) is passed as there are no existing InterventionPointUrls for a new intervention_point
    context = {"tracks" : [(t, None) for t in
                           Track.objects.filter(course_id=course_id)],
               "cancel_url": "/#tabs-2"}
    return render_to_response("ab_tool/edit_intervention_point.html", context)


@lti_role_required(ADMINS)
def submit_create_intervention_point(request):
    """ Note: request will always be POST because Canvas fetches pages within iframe by POST
        TODO: use Django forms library to save instead of getting individual POST params """
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    t = InterventionPoint.objects.create(name=name, notes=notes, course_id=course_id)
    intervention_pointurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in intervention_pointurls:
        _,track_id = k.split(STAGE_URL_TAG)
        is_canvas = post_param(request, DEPLOY_OPTION_TAG + track_id)
        as_tab = request.POST.get(AS_TAB_TAG + track_id, None)
        is_canvas_page = bool(is_canvas == "canvas_url")
        open_as_tab = bool(as_tab == "true")
        InterventionPointUrl.objects.create(url=format_url(v), intervention_point_id=t.id, track_id=track_id,
                                is_canvas_page=is_canvas_page, open_as_tab=open_as_tab)
    return redirect("/#tabs-2")


@lti_role_required(ADMINS)
def modules_page_edit_intervention_point(request, intervention_point_id):
    context = edit_intervention_point_common(request, intervention_point_id)
    return render_to_response("ab_tool/modules_page_edit_intervention_point.html", context)

@lti_role_required(ADMINS)
def edit_intervention_point(request, intervention_point_id):
    context = edit_intervention_point_common(request, intervention_point_id)
    context["cancel_url"] = "/#tabs-2"
    return render_to_response("ab_tool/edit_intervention_point.html", context)

def edit_intervention_point_common(request, intervention_point_id):
    """ Common core shared bewteen edit_intervention_point and modules_page_edit_intervention_point """
    intervention_point = get_object_or_404(InterventionPoint, pk=intervention_point_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if course_id != intervention_point.course_id:
        raise UNAUTHORIZED_ACCESS
    all_tracks = Track.objects.filter(course_id=course_id)
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
               "is_installed": intervention_point_is_installed(request, intervention_point),
               #TODO: "installed_module": installed_module,
               }
    return context


@lti_role_required(ADMINS)
def submit_edit_intervention_point(request, intervention_point_id):
    """ Note: Only allowed if admin has privileges on the particular course.
        TODO: consider using Django forms to save rather of getting individual POST params """
    intervention_point = get_object_or_404(InterventionPoint, pk=intervention_point_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    name = post_param(request, "name")
    notes = post_param(request, "notes")
    if course_id != intervention_point.course_id:
        raise UNAUTHORIZED_ACCESS
    intervention_point.update(name=name, notes=notes)
    # InterventionPointUrl creation
    intervention_pointurls = [(k,v) for (k,v) in request.POST.iteritems() if STAGE_URL_TAG in k and v]
    for (k,v) in intervention_pointurls:
        _, track_id = k.split(STAGE_URL_TAG)
        # This is a search for the joint unique index of InterventionPointUrl, so it
        # should not ever return multiple objects
        is_canvas = post_param(request, DEPLOY_OPTION_TAG + track_id)
        as_tab = request.POST.get(AS_TAB_TAG + track_id, None)
        is_canvas_page = bool(is_canvas == "canvas_url")
        open_as_tab = bool(as_tab == "true")
        try:
            intervention_point_url = InterventionPointUrl.objects.get(intervention_point__pk=intervention_point_id, track__pk=track_id)
            intervention_point_url.update(url=format_url(v), is_canvas_page=is_canvas_page, open_as_tab=open_as_tab)
        except InterventionPointUrl.DoesNotExist:
            InterventionPointUrl.objects.create(url=format_url(v), intervention_point_id=intervention_point_id, track_id=track_id,
                                    is_canvas_page=is_canvas_page, open_as_tab=open_as_tab)
    return redirect("/#tabs-2")


@lti_role_required(ADMINS)
def delete_intervention_point(request, intervention_point_id):
    """ Note: Installed intervention_points are not allowed to be deleted
        Note: attached InterventionPointUrls are deleted via cascading delete """
    intervention_point = get_object_or_404(InterventionPoint, pk=intervention_point_id)
    course_id = get_lti_param(request, "custom_canvas_course_id")
    if course_id != intervention_point.course_id:
        raise UNAUTHORIZED_ACCESS
    if intervention_point_is_installed(request, intervention_point):
        raise DELETING_INSTALLED_STAGE
    intervention_point.delete()
    return redirect("/#tabs-2")