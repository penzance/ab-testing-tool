from django.conf import settings
from django.test import TestCase
from django.utils.importlib import import_module
from json import dumps
from mock import patch, MagicMock

from ab_testing_tool.constants import ADMINS


LIST_MODULES = "canvas_sdk.methods.modules.list_modules"
LIST_ITEMS = "canvas_sdk.methods.modules.list_module_items"
 
TEST_COURSE_ID = "12345"
TEST_OTHER_COURSE_ID = "5555555"
TEST_DOMAIN = "example.com"


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
        ]
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)
    
    def set_roles(self, roles):
        session = self.client.session
        session["LTI_LAUNCH"]["roles"] = roles
        session.save()
    
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
        self.assertRaises(exception_instance.__class__, func, *args, **kwargs)
        try:
            func(*args, **kwargs)
            assert False, "Function either raises no exception or is non-deterministic"
        except Exception as e:
            self.assertEquals(str(e), str(exception_instance))

class APIReturn(object):
    """Spoofs returned response from Canvas SDK. Has response.ok property and JSON contents"""
    def __init__(self, obj, ok=True):
        self.text = dumps(obj)
        self.ok = ok
