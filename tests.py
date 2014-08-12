from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.importlib import import_module
from json import dumps
from mock import patch, MagicMock

from ab_testing_tool.views import ADMINS
from ab_testing_tool.controllers import get_uninstalled_treatments,\
    treatment_url
from ab_testing_tool.models import Treatment

VIEWS_LIST_MODULES = "ab_testing_tool.views.list_modules"
CONTROLLERS_LIST_MODULES = "ab_testing_tool.controllers.list_modules"
CONTROLLERS_LIST_ITEMS = "ab_testing_tool.controllers.list_module_items"


class SessionTestCase(TestCase):
    def setUp(self):
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
        
        lti_launch = {}
        lti_launch['roles'] = ADMINS
        lti_launch['custom_canvas_course_id'] = '12345'
        lti_launch['lis_course_offering_sourcedid'] = '92345'
        lti_launch['custom_canvas_api_domain'] = "example.com"
        lti_launch["launch_presentation_return_url"] = "example.com"
        session = self.client.session
        session['LTI_LAUNCH'] = lti_launch
        session.save()
        
        self.request = MagicMock()
        self.request.session = session
        self.request.get_host = MagicMock(return_value="example.com")
    
    def set_roles(self, roles):
        session = self.client.session
        session['LTI_LAUNCH']["roles"] = roles
        session.save()


class APIReturn(object):
    def __init__(self, obj, ok=True):
        self.text = dumps(obj)
        self.ok = ok


class test_views(SessionTestCase):
    @patch(VIEWS_LIST_MODULES, return_value=APIReturn([]))
    @patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([]))
    def test_index(self, _mock1, _mock2):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "control_panel.html")
    
    @patch(CONTROLLERS_LIST_ITEMS, return_value=APIReturn([]))
    @patch(VIEWS_LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    @patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_index_with_module(self, _mock1, _mock2, _mock3):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "control_panel.html")
    
    @patch(CONTROLLERS_LIST_ITEMS, return_value=APIReturn([]))
    @patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([]))
    def test_get_uninstalled_treatments(self, _mock1, _mock2):
        treatments = get_uninstalled_treatments(self.request)
        self.assertEqual(len(treatments), 0)
    
    @patch(CONTROLLERS_LIST_ITEMS, return_value=APIReturn([]))
    @patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_treatments_with_item(self, _mock1, _mock2):
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
