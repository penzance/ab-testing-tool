from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.importlib import import_module
from json import dumps
from mock import patch, MagicMock

from ab_testing_tool.pages.main_pages import ADMINS
from ab_testing_tool.controllers import (stage_url, get_full_host)
from ab_testing_tool.canvas import InvalidResponseError, parse_response

LIST_MODULES = "canvas_sdk.methods.modules.list_modules"
LIST_ITEMS = "canvas_sdk.methods.modules.list_module_items"
 
TEST_COURSE_ID = "12345"

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
        lti_launch["custom_canvas_api_domain"] = "example.com"
        lti_launch["launch_presentation_return_url"] = "example.com"
        session = self.client.session
        session["LTI_LAUNCH"] = lti_launch
        session.save()
        
        self.request = MagicMock()
        self.request.session = session
        self.request.get_host = MagicMock(return_value="example.com")
        
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


class APIReturn(object):
    """Spoofs returned response from Canvas SDK. Has response.ok property and JSON contents"""
    def __init__(self, obj, ok=True):
        self.text = dumps(obj)
        self.ok = ok


class test_main_pages(SessionTestCase):
    """Tests related to control panel and main pages and genearl backend methods"""
    def test_index_and_control_panel_view(self):
        """Tests control_panel template renders when authenticated and with no
            contents returned from Canvas"""
        response = self.client.get(reverse("index"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "control_panel.html")
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_control_panel_with_module_and_item(self, _mock1):
        """Tests control_panel template renders with items returned from Canvas"""
        mock_item = {"type": "ExternalTool",
                     "external_url": stage_url(self.request, 0)}
        api_return = APIReturn([mock_item])
        with patch(LIST_ITEMS, return_value=api_return):
            response = self.client.get(reverse("index"), follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "control_panel.html")
    
    def test_unauthenticated_index(self):
        """Tests control_panel template does not render when unauthorized"""
        self.set_roles([])
        response = self.client.get(reverse("index"), follow=True)
        self.assertTemplateNotUsed(response, "control_panel.html")
    
    def test_get_full_host(self):
        """ Tests that appropriate prefix of http/https is used based on whether SSL is used"""
        self.request.is_secure.return_value = False
        self.assertIn("http://", get_full_host(self.request))
        self.request.is_secure.return_value = True
        self.assertIn("https://", get_full_host(self.request))
    
    def test_parse_response_error(self):
        """ Tests that a not OK API response raises an InvalidResponseError"""
        response = APIReturn([])
        response.ok = False
        self.assertRaises(InvalidResponseError, parse_response, response)
    
    def test_parse_response(self):
        """ Tests that an OK API response is correctly returned"""
        json_obj = [{"id": 0}]
        response = APIReturn(json_obj)
        response.ok = True
        self.assertEquals(parse_response(response), json_obj)
    
    def test_tool_config(self):
        """ Tests that that tool_config page returns XML content"""
        response = self.client.get(reverse("tool_config"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers["content-type"],
                        ('Content-Type', 'text/xml'))

