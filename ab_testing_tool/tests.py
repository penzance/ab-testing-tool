from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.importlib import import_module
from json import dumps
from mock import patch, MagicMock

from ab_testing_tool.pages.main_pages import ADMINS, STAGE_URL_TAG
from ab_testing_tool.controllers import (get_uninstalled_stages,
    stage_url, get_full_host)
from ab_testing_tool.models import Stage, StageUrl
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


class test_views(SessionTestCase):
    def test_index(self):
        """Tests control_panel template rendered with nothing returned from Canvas"""
        response = self.client.get(reverse("index"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "control_panel.html")

    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_index_with_module_and_item(self, _mock1):
        """Tests control_panel template rendered with items returned from Canvas"""
        mock_item = {"type": "ExternalTool",
                     "external_url": stage_url(self.request, 0)}
        api_return = APIReturn([mock_item])
        with patch(LIST_ITEMS, return_value=api_return):
            response = self.client.get(reverse("index"), follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "control_panel.html")

    def test_unauthenticated_index(self):
        """Tests control_panel template not rendered when unauthorized"""
        self.set_roles([])
        response = self.client.get(reverse("index"), follow=True)
        self.assertTemplateNotUsed(response, "control_panel.html")

    def test_get_uninstalled_stages(self):
        """Tests method get_uninstalled_stages runs and returns no stages when database empty"""
        stages = get_uninstalled_stages(self.request)
        self.assertEqual(len(stages), 0)

    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_with_item(self, _mock1):
        """Tests method get_uninstalled_stages returns one when database has one item"""
        #TODO !! take into account course_id here!!
        Stage.objects.create(name="stage1")
        stages = get_uninstalled_stages(self.request)
        self.assertEqual(len(stages), 1)

    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_against_api(self, _mock1):
        """ Tests method get_uninstalled_stages returns zero when stage in database
            is also returned by the API, which means it is installed """
        stage = Stage.objects.create(name="stage1")
        mock_item = {"type": "ExternalTool",
                     "external_url": stage_url(self.request, stage.id)}
        with patch(LIST_ITEMS, return_value=APIReturn([mock_item])):
            stages = get_uninstalled_stages(self.request)
            self.assertEqual(len(stages), 0)

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

    def test_submit_create_stage(self):
        #TODO: change this test to several tests that Stage and StageUrls in DB,
        #covering the cases when no stage urls submited, with stage urls are submitted
        """Tests that create_stage creates a Stage object verified by DB count"""
        num_stages = Stage.objects.count()
        data = {"name": "stage", "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(num_stages + 1, Stage.objects.count())

    def test_submit_create_stage_with_stageurls(self):
        """Tests that create_stage creates a Stage object and StageUrl objects
            verified by DB count"""
        num_stages = Stage.objects.count()
        num_stageurls = StageUrl.objects.count()
        data = {"name": "stage", STAGE_URL_TAG + "1": "http://example.com/page",
                STAGE_URL_TAG + "2": "http://example.com/otherpage", "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(num_stages + 1, Stage.objects.count())
        self.assertEquals(num_stageurls + 2, Stage.objects.count())

    def test_submit_edit_stage(self):
        """ Tests that edit_stage does not change DB count but does change Stage
            attribute"""
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
        """ Tests that update_stage method raises error for non-existent Stage """
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": 10000987}
        self.assertRaises(Exception, self.client.post,
                          reverse("submit_edit_stage"), data, follow=True)

    def test_submit_edit_stage_wrong_course(self):
        """ Tests that update_stage method raises error for existent Stage but
            for wrong course"""
        #TODO: make similar test for update_tracks
        #TODO: render template tests for all the forms
        stage = Stage.objects.create(name="old_name",
                                             course_id="other_course")
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": stage.id}
        self.assertRaises(Exception, self.client.post,
                          reverse("submit_edit_stage"), data, follow=True)

    def test_tool_config(self):
        """ Tests that that tool_config page returns XML content"""
        response = self.client.get(reverse("tool_config"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers["content-type"],
                        ('Content-Type', 'text/xml'))
