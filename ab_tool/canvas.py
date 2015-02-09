from canvas_sdk.methods import modules
from canvas_sdk import RequestContext
from canvas_sdk.exceptions import CanvasAPIError
from django.conf import settings

from ab_tool.exceptions import (MISSING_LTI_PARAM, MISSING_LTI_LAUNCH,
    NO_SDK_RESPONSE)
from django_canvas_oauth import get_token
from ab_tool.controllers import intervention_point_url
from ab_tool.models import InterventionPoint, Experiment
from django_canvas_oauth.exceptions import NewTokenNeeded


class CanvasModules(object):
    
    def __init__(self, request):
        self.request_context = get_canvas_request_context(request)
        self.course_id = get_lti_param(request, "custom_canvas_course_id")
        # Only pass this attribute to intervention_point_url
        self.request = request
        # self.modules is a list of module dicts
        self.modules = list_modules(self.request_context, self.course_id)
        for module in self.modules:
            module["module_items"] = list_module_items(
                    self.request_context, self.course_id, module["id"])
    
    def get_uninstalled_intervention_points(self):
        """ Returns the list of InterventionPoint objects that have been created for the
            current course but not installed in any of that course's modules """
        installed_intervention_point_urls = self._get_installed_intervention_point_urls()
        intervention_points = [intervention_point for intervention_point in
                               InterventionPoint.objects.filter(course_id=self.course_id)
                               if intervention_point_url(self.request, intervention_point.id)
                               not in installed_intervention_point_urls]
        return intervention_points
    
    def get_deletable_experiment_ids(self):
        """ Returns list of experiment ids for experiments that can be deleted
            (they have tracks_finalzed == False and no installed intervention
            points """
        return [e.id for e in Experiment.objects.filter(course_id=self.course_id)
                if not e.tracks_finalized
                and not self.experiment_has_installed_intervention(e)]
    
    def intervention_point_is_installed(self, intervention_point):
        return (intervention_point_url(self.request, intervention_point.id) in
                self._get_installed_intervention_point_urls())
    
    def experiment_has_installed_intervention(self, experiment):
        """ Checks to see if a experiment has any intervention points installed.
            For Python2.6+, the built-in isdisjoint provides the fastest return"""
        return not set([intervention_point_url(self.request, ip.id) for ip in
               experiment.intervention_points.all()]).isdisjoint(set(self._get_installed_intervention_point_urls()))
    
    def get_modules_with_items(self):
        """ Returns a list of all modules with the items of that module added to the
            module under the extra attribute "module_items" (this is a list).
            Each item in those lists has the added attribute "is_intervention_point",
            which is a boolean describing whether or not the item is a intervention_point
            of the ab_testing_tool """
        intervention_point_urls = self._all_intervention_point_urls()
        for module in self.modules:
            for item in module["module_items"]:
                is_intervention_point = (item["type"] == "ExternalTool" and "external_url" in item
                            and item["external_url"] in intervention_point_urls)
                item["is_intervention_point"] = is_intervention_point
                if is_intervention_point:
                    item["database_name"] = intervention_point_urls[item["external_url"]].name
                    item["experiment_name"] = intervention_point_urls[item["external_url"]].experiment.name
        return self.modules
    
    def _all_intervention_point_urls(self):
        """ Returns a dict of deploy urls to intervention points of all intervention_points
            in the database for that course"""
        return {intervention_point_url(self.request, intervention_point.id): intervention_point
                for intervention_point in InterventionPoint.objects.filter(course_id=self.course_id)}
    
    def _get_installed_intervention_point_urls(self):
        """ Returns the list of InterventionPointUrls (as strings) for InterventionPoints
            that have been installed in at least one of the courses modules. """
        installed_intervention_point_urls = []
        for module in self.modules:
            intervention_point_urls = [item["external_url"] for item in module["module_items"]
                          if item["type"] == "ExternalTool"]
            installed_intervention_point_urls.extend(intervention_point_urls)
        return installed_intervention_point_urls


def list_module_items(request_context, course_id, module_id):
    try:
        return modules.list_module_items(request_context, course_id, module_id,
                                         "content_details").json()
    except CanvasAPIError as exception:
        handle_canvas_error(exception)

def list_modules(request_context, course_id):
    try:
        return modules.list_modules(request_context, course_id,
                                    "content_details").json()
    except CanvasAPIError as exception:
        handle_canvas_error(exception)


def get_lti_param(request, key):
    """
    Note: Not Canvas related, but located here to avoid cyclic imports
    TODO: Add this function to Django auth lti library
    """
    if "LTI_LAUNCH" not in request.session:
        raise MISSING_LTI_LAUNCH
    if key not in request.session["LTI_LAUNCH"]:
        raise MISSING_LTI_PARAM
    return request.session["LTI_LAUNCH"][key]


def get_canvas_request_context(request):
    # FOR LOCAL DEVLEOPEMENT PURPOSES. TODO: Remove if-block in production.
    if "course_oauth_token" in settings.SECURE_SETTINGS:
        oauth_token = settings.SECURE_SETTINGS["course_oauth_token"]
    else:
        oauth_token = get_token(request)
    canvas_domain = get_lti_param(request, "custom_canvas_api_domain")
    canvas_url = "https://%s/api" % (canvas_domain)
    return RequestContext(oauth_token, canvas_url)


def handle_canvas_error(exception):
    if exception.status_code == 401:
        raise NewTokenNeeded("Your canvas oauth token is invalid")
    raise NO_SDK_RESPONSE
