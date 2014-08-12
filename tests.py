from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.importlib import import_module
from json import dumps
from mock import patch, MagicMock

from ab_testing_tool.views import ADMINS
from ab_testing_tool.controllers import get_uninstalled_treatments,\
    treatment_url, get_full_host, parse_response, InvalidResponseError
from ab_testing_tool.models import Treatment

VIEWS_LIST_MODULES = "ab_testing_tool.views.list_modules"
CONTROLLERS_LIST_MODULES = "ab_testing_tool.controllers.list_modules"
CONTROLLERS_LIST_ITEMS = "ab_testing_tool.controllers.list_module_items"

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
            patch(VIEWS_LIST_MODULES, return_value=APIReturn([])),
            patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([])),
            patch(CONTROLLERS_LIST_ITEMS, return_value=APIReturn([])),
        ]
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)
    
    def set_roles(self, roles):
        session = self.client.session
        session["LTI_LAUNCH"]["roles"] = roles
        session.save()


class APIReturn(object):
    def __init__(self, obj, ok=True):
        self.text = dumps(obj)
        self.ok = ok


class test_views(SessionTestCase):
    def test_index(self):
        response = self.client.get(reverse("index"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "control_panel.html")
    
    @patch(VIEWS_LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    @patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_index_with_module_and_item(self, _mock1, _mock2):
        mock_item = {"type": "ExternalTool",
                     "external_url": treatment_url(self.request, 0)}
        with patch(CONTROLLERS_LIST_ITEMS, return_value=APIReturn([mock_item])):
            response = self.client.get(reverse("index"), follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "control_panel.html")
    
    def test_get_uninstalled_treatments(self):
        treatments = get_uninstalled_treatments(self.request)
        self.assertEqual(len(treatments), 0)
    
    @patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_treatments_with_item(self, _mock1):
        Treatment.objects.create(name="treatment1")
        treatments = get_uninstalled_treatments(self.request)
        self.assertEqual(len(treatments), 1)
    
    @patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_treatments_against_api(self, _mock1):
        treatment = Treatment.objects.create(name="treatment1")
        mock_item = {"type": "ExternalTool",
                     "external_url": treatment_url(self.request, treatment.id)}
        with patch(CONTROLLERS_LIST_ITEMS, return_value=APIReturn([mock_item])):
            treatments = get_uninstalled_treatments(self.request)
            self.assertEqual(len(treatments), 0)
    
    def test_get_full_host(self):
        self.request.is_secure.return_value = False
        self.assertIn("http://", get_full_host(self.request))
        self.request.is_secure.return_value = True
        self.assertIn("https://", get_full_host(self.request))
    
    def test_parse_response(self):
        response = APIReturn([])
        response.ok = False
        self.assertRaises(InvalidResponseError, parse_response, response)
    
    def test_create_treatment(self):
        num_treatments = Treatment.objects.count()
        data = {"name": "treatment", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": ""}
        response = self.client.post(reverse("create_treatment"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(num_treatments + 1, Treatment.objects.count())
    
    def test_update_treatment(self):
        treatment = Treatment.objects.create(name="old_name",
                                             course_id=TEST_COURSE_ID)
        treatment_id = treatment.id
        num_treatments = Treatment.objects.count()
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": treatment_id}
        response = self.client.post(reverse("update_treatment"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(num_treatments, Treatment.objects.count())
        treatment = Treatment.objects.get(id=treatment_id)
        self.assertEquals(treatment.name, "new_name")
    
    def test_update_nonexistent_treatment(self):
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": 10000987}
        self.assertRaises(Exception, self.client.post,
                          reverse("update_treatment"), data, follow=True)
    
    def test_update_treatment_wrong_course(self):
        treatment = Treatment.objects.create(name="old_name",
                                             course_id="other_course")
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": treatment.id}
        self.assertRaises(Exception, self.client.post,
                          reverse("update_treatment"), data, follow=True)
