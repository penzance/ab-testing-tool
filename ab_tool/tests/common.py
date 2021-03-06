from django.conf import settings
from django.test import TestCase
from django.utils.importlib import import_module
from json import dumps
from mock import patch, MagicMock

from ab_tool.constants import ADMINS
from ab_tool.models import (Experiment, Track, InterventionPoint,
    TrackProbabilityWeight)
from error_middleware.exceptions import DEFAULT_ERROR_STATUS, RenderableError
from error_middleware.middleware import ERROR_TEMPLATE


LIST_MODULES = "canvas_sdk.methods.modules.list_modules"
LIST_ITEMS = "canvas_sdk.methods.modules.list_module_items"
GET_TOKEN = "ab_tool.canvas.get_token"

TEST_COURSE_ID = "12345"
TEST_OTHER_COURSE_ID = "5555555"
TEST_DOMAIN = "example.com"
TEST_STUDENT_ID = "70707707"
TEST_EMAIL = "test@example.com"
TEST_STUDENT_NAME = "Test Student"

NONEXISTENT_INTERVENTION_POINT_ID = 12345678987654321 #111111111^2
NONEXISTENT_TRACK_ID = 31415926535897932 #pi

NONEXISTENT_EXPERIMENT_ID = 31415926535897932 #pi

class RequestMock(MagicMock):
    get_host = MagicMock(return_value=TEST_DOMAIN)
    
    def build_absolute_uri(self, location):
        http = "https://" if self.is_secure() else "http://"
        return "%s%s%s" % (http, self.get_host(), location)


class SessionTestCase(TestCase):
    def setUp(self):
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = "django.contrib.sessions.backends.file"
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
        
        settings.LOGGING = {}
        
        lti_launch = {}
        lti_launch["roles"] = ADMINS
        lti_launch["custom_canvas_course_id"] = TEST_COURSE_ID
        lti_launch["lis_course_offering_sourcedid"] = "92345"
        lti_launch["custom_canvas_api_domain"] = TEST_DOMAIN
        lti_launch["launch_presentation_return_url"] = TEST_DOMAIN
        lti_launch["custom_canvas_user_login_id"] = TEST_STUDENT_ID
        lti_launch["lis_person_name_full"] = TEST_STUDENT_NAME
        lti_launch["context_title"] = "Course title"
        lti_launch["lis_person_contact_email_primary"] = TEST_EMAIL
        session = self.client.session
        session["LTI_LAUNCH"] = lti_launch
        session.save()
        
        self.request = RequestMock()
        self.request.session = session
        
        # Patches api functions for all tests; can be overridden by re-patching
        # the particular api call for a particular test
        patchers = [
            patch(LIST_MODULES, return_value=APIReturn([])),
            patch(LIST_ITEMS, return_value=APIReturn([])),
            patch(GET_TOKEN, return_value="MOCK_TOKEN"),
        ]
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)
    
    def set_lti_param(self, param_name, param_value):
        """ Convenience method to set an LIT_LAUNCH parameter in the mock session """
        session = self.client.session
        session["LTI_LAUNCH"][param_name] = param_value
        session.save()
    
    def set_roles(self, roles):
        self.set_lti_param("roles", roles)
    
    def assertOkay(self, response):
        self.assertEqual(response.status_code, 200)
    
    def assertError(self, response, exception_instance):
        self.assertTemplateUsed(response, ERROR_TEMPLATE)
        if isinstance(exception_instance, RenderableError):
            self.assertEqual(response.status_code, exception_instance.status_code)
        else:
            self.assertEqual(response.status_code, DEFAULT_ERROR_STATUS)
        self.assertIn("message", response.context)
        self.assertEqual(response.context["message"], str(exception_instance))
    
    def assertSameIds(self, iterable_1, iterable_2, duplicates_allowed=False):
        """ Checks that the two iterables have the same set of .id attributes
            among their items; if duplicates_allowed is False, the test
            will pass if either iterable contains duplicate_ids within itself """
        ids_1 = [i.id for i in iterable_1]
        ids_2 = [i.id for i in iterable_2]
        if not duplicates_allowed:
            self.assertEqual(len(set(ids_1)), len(ids_1))
            self.assertEqual(len(set(ids_2)), len(ids_2))
        self.assertEqual(set(ids_1), set(ids_2))
    
    def assertRaisesSpecific(self, exception_instance, func, *args, **kwargs):
        """ Asserts that the function with the passed args and kwargs,
            raises an exception that matches the exception_instance.
            Match means has the same message, and is either the same class as
            exception_instance or a child of exception_instance's class. """
        error = False
        self.assertRaises(exception_instance.__class__, func, *args, **kwargs)
        try:
            func(*args, **kwargs)
            error = True
            
        except Exception as e:
            self.assertEquals(str(e), str(exception_instance))
        if error:
            raise Exception("Function either raises no exception or is "
                            "non-deterministic")
    
    def create_test_experiment(self, course_id=TEST_COURSE_ID, name="testexperiment",
                               assignment_method=Experiment.UNIFORM_RANDOM, **kwargs):
        return Experiment.objects.create(name=name, course_id=course_id,
                                         assignment_method=assignment_method,
                                         **kwargs)
    
    def create_test_track(self, course_id=TEST_COURSE_ID, name="testtrack", experiment=None):
        if not experiment:
            experiment = Experiment.get_placeholder_course_experiment(course_id)
        return Track.objects.create(name=name, course_id=course_id,
                                    experiment=experiment)
    
    def create_test_track_weight(self, course_id=TEST_COURSE_ID, weighting=1,
                                 track=None, experiment=None):
        if not experiment:
            experiment = Experiment.get_placeholder_course_experiment(course_id)
        if not track:
            track = Track.objects.create(name="testtrack", course_id=course_id,
                                         experiment=experiment)
        return TrackProbabilityWeight.objects.create(
                course_id=course_id, weighting=weighting, track=track,
                experiment=experiment)
    
    def create_test_intervention_point(self, course_id=TEST_COURSE_ID, name="testip",
                                       experiment=None):
        if not experiment:
            experiment = Experiment.get_placeholder_course_experiment(course_id)
        return InterventionPoint.objects.create(name=name, course_id=course_id,
                                                experiment=experiment)


class APIReturn(object):
    """ Spoofs returned response from Canvas SDK. Has response.ok property and
        JSON contents """
    def __init__(self, obj, ok=True):
        self.obj = obj
        self.text = dumps(obj)
        self.ok = ok
        
    def json(self):
        return self.obj
