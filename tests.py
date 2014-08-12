from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.importlib import import_module
from json import dumps
from mock import patch

from ab_testing_tool.views import ADMINS


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


class test_views(SessionTestCase):
    
    @patch("ab_testing_tool.views.list_modules")
    @patch("ab_testing_tool.controllers.list_modules")
    def test_index(self, list_modules_mock1, list_modules_mock2):
        list_modules_mock1.return_value.text = dumps([])
        list_modules_mock2.return_value.text = dumps([])
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "control_panel.html")
    
    @patch("ab_testing_tool.controllers.list_module_items")
    @patch("ab_testing_tool.views.list_modules")
    @patch("ab_testing_tool.controllers.list_modules")
    def test_index_with_module(self, list_modules_mock1, list_modules_mock2,
                               list_module_items_mock):
        list_module_ret = dumps([{"id": 0}])
        list_modules_mock1.return_value.text = list_module_ret
        list_modules_mock2.return_value.text = list_module_ret
        list_module_items_mock.return_value.text = dumps([])
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "control_panel.html")
