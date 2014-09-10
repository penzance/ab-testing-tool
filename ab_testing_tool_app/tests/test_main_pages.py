from django.core.urlresolvers import reverse
from mock import patch

from ab_testing_tool_app.controllers import stage_url, get_uninstalled_stages
from ab_testing_tool_app.tests.common import (SessionTestCase, LIST_MODULES,
    LIST_ITEMS, APIReturn, TEST_COURSE_ID, TEST_OTHER_COURSE_ID)
from ab_testing_tool_app.models import Stage, Track
from ab_testing_tool_app.views.main_pages import tool_config


class TestMainPages(SessionTestCase):
    """ Tests related to control panel and main pages """
    
    def test_not_authorized_renders(self):
        """ Tests that the not_authorized page renders """
        response = self.client.get(reverse("not_authorized"), follow=True)
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_index_and_control_panel_view(self):
        """ Tests control_panel template renders when authenticated and with no
            contents returned from Canvas"""
        response = self.client.get(reverse("index"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "control_panel.html")
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_control_panel_with_module_and_item(self, _mock1):
        """ Tests control_panel template renders with items returned from Canvas"""
        mock_item = {"type": "ExternalTool",
                     "external_url": stage_url(self.request, 0)}
        api_return = APIReturn([mock_item])
        with patch(LIST_ITEMS, return_value=api_return):
            response = self.client.get(reverse("index"), follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "control_panel.html")
    
    def test_unauthenticated_index(self):
        """ Tests control_panel template does not render when unauthorized"""
        self.set_roles([])
        response = self.client.get(reverse("index"), follow=True)
        self.assertTemplateNotUsed(response, "control_panel.html")
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_index_context(self):
        """ Checks that the context of the index contains the relevant fields """
        response = self.client.get(reverse("index"), follow=True)
        self.assertIn("stages", response.context)
        self.assertIn("modules", response.context)
        self.assertIn("uninstalled_stages", response.context)
        self.assertIn("tracks", response.context)
        self.assertIn("canvas_url", response.context)
    
    def test_index_context_stages_and_tracks(self):
        """ Checks that the stages and tracks passed to the index template
            contain values from the database """
        response = self.client.get(reverse("index"), follow=True)
        self.assertEqual(len(response.context["stages"]), 0)
        self.assertEqual(len(response.context["tracks"]), 0)
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("index"), follow=True)
        self.assertEqual(len(response.context["stages"]), 1)
        self.assertEqual(len(response.context["tracks"]), 1)
        self.assertSameIds([stage], response.context["stages"])
        self.assertSameIds([track], response.context["tracks"])
    
    def test_index_context_course_specific_stages_and_tracks(self):
        """ Checks that the stages and tracks passed to the index template
            only contain database values matching the course_id """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        Stage.objects.create(name="stage1", course_id=TEST_OTHER_COURSE_ID)
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        Track.objects.create(name="track2", course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("index"), follow=True)
        self.assertEqual(len(response.context["stages"]), 1)
        self.assertEqual(len(response.context["tracks"]), 1)
        self.assertSameIds([stage], response.context["stages"])
        self.assertSameIds([track], response.context["tracks"])
    
    def test_index_context_uninstalled_stages(self):
        """ Tests that the context for the index correctly contains
            the uninstalled stages for the course """
        stage1 =Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        stage2 = Stage.objects.create(name="stage2", course_id=TEST_COURSE_ID)
        with patch("ab_testing_tool_app.views.main_pages.get_uninstalled_stages",
                   return_value=[stage1]):
            response = self.client.get(reverse("index"), follow=True)
            self.assertSameIds(response.context["uninstalled_stages"], [stage1])
            self.assertSameIds(response.context["stages"], [stage1, stage2])
    
    def test_index_context_modules(self):
        ret_val = [{"name": "module1"}]
        with patch("ab_testing_tool_app.views.main_pages.get_modules_with_items",
                   return_value=ret_val):
            response = self.client.get(reverse("index"), follow=True)
            self.assertEqual(response.context["modules"], ret_val)
    
    def test_tool_config(self):
        """ Tests that that tool_config page returns XML content"""
        response = self.client.get(reverse("tool_config"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers["content-type"],
                        ('Content-Type', 'text/xml'))
    
    def test_too_config_urls(self):
        """ Tests that urls for index and resource_selection appear in
            the return of tool config; this test doesn't use self.client
            in order to use the same request for building the comparison uris
            as it does for calling the view """
        index_url = self.request.build_absolute_uri(reverse("index"))
        resource_selection_url = self.request.build_absolute_uri(
                reverse("resource_selection"))
        response = tool_config(self.request)
        self.assertContains(response, index_url)
        self.assertContains(response, resource_selection_url)
