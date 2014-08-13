from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.importlib import import_module
from json import dumps
from mock import patch, MagicMock

from ab_testing_tool.pages.main_pages import ADMINS
from ab_testing_tool.controllers import (get_uninstalled_stages,
    stage_url, get_full_host, parse_response, InvalidResponseError)
from ab_testing_tool.models import Stage

VIEWS_LIST_MODULES = "ab_testing_tool.pages.main_pages.list_modules"
VIEWS_LIST_ITEMS = "ab_testing_tool.pages.main_pages.list_module_items"
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
            patch(VIEWS_LIST_ITEMS, return_value=APIReturn([])),
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
                     "external_url": stage_url(self.request, 0)}
        api_return = APIReturn([mock_item])
        with patch(CONTROLLERS_LIST_ITEMS, return_value=api_return):
            with patch(VIEWS_LIST_ITEMS, return_value=api_return):
                response = self.client.get(reverse("index"), follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "control_panel.html")

    def test_unauthenticated_index(self):
        self.set_roles([])
        response = self.client.get(reverse("index"), follow=True)
        self.assertTemplateNotUsed(response, "control_panel.html")

    def test_get_uninstalled_stages(self):
        stages = get_uninstalled_stages(self.request)
        self.assertEqual(len(stages), 0)

    @patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_with_item(self, _mock1):
        Stage.objects.create(name="stage1")
        stages = get_uninstalled_stages(self.request)
        self.assertEqual(len(stages), 1)

    @patch(CONTROLLERS_LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_against_api(self, _mock1):
        stage = Stage.objects.create(name="stage1")
        mock_item = {"type": "ExternalTool",
                     "external_url": stage_url(self.request, stage.id)}
        with patch(CONTROLLERS_LIST_ITEMS, return_value=APIReturn([mock_item])):
            stages = get_uninstalled_stages(self.request)
            self.assertEqual(len(stages), 0)

    def test_get_full_host(self):
        self.request.is_secure.return_value = False
        self.assertIn("http://", get_full_host(self.request))
        self.request.is_secure.return_value = True
        self.assertIn("https://", get_full_host(self.request))

    def test_parse_response(self):
        response = APIReturn([])
        response.ok = False
        self.assertRaises(InvalidResponseError, parse_response, response)

    def test_submit_create_stage(self):
        num_stages = Stage.objects.count()
        data = {"name": "stage", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": ""}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(num_stages + 1, Stage.objects.count())

    def test_submit_edit_stage(self):
        stage = Stage.objects.create(name="old_name",
                                             course_id=TEST_COURSE_ID)
        stage_id = stage.id
        num_stages = Stage.objects.count()
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": stage_id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(num_stages, Stage.objects.count())
        stage = Stage.objects.get(id=stage_id)
        self.assertEquals(stage.name, "new_name")

    def test_update_nonexistent_stage(self):
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": 10000987}
        self.assertRaises(Exception, self.client.post,
                          reverse("submit_edit_stage"), data, follow=True)

    def test_submit_edit_stage_wrong_course(self):
        stage = Stage.objects.create(name="old_name",
                                             course_id="other_course")
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": stage.id}
        self.assertRaises(Exception, self.client.post,
                          reverse("submit_edit_stage"), data, follow=True)

    def test_tool_config(self):
        response = self.client.get(reverse("tool_config"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers["content-type"],
                        ('Content-Type', 'text/xml'))
