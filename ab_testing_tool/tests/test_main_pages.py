from django.core.urlresolvers import reverse
from mock import patch

from ab_testing_tool.controllers import stage_url
from ab_testing_tool.tests.common import (SessionTestCase, LIST_MODULES,
    LIST_ITEMS, APIReturn)


class test_main_pages(SessionTestCase):
    """Tests related to control panel and main pages and general backend methods"""
    
    def test_not_authorized_renders(self):
        """ Tests that the not_authorized page renders """
        response = self.client.get(reverse("not_authorized"), follow=True)
        self.assertEqual(response.status_code, 200)
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
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_tool_config(self):
        """ Tests that that tool_config page returns XML content"""
        response = self.client.get(reverse("tool_config"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers["content-type"],
                        ('Content-Type', 'text/xml'))

