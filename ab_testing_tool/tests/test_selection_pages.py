from django.core.urlresolvers import reverse
from ab_testing_tool.tests.common import SessionTestCase

class test_selection_pages(SessionTestCase):
    """Tests related to selection pages and methods"""

    def test_resource_selection_view(self):
        #TODO: check ext_content_return_types,content_return_url, content_return_url, stages, tracks, HttpResponse Errors
        """Tests add_module_item template renders for url 'resource_selection' when authenticated"""
        self.request.session["LTI_LAUNCH"]["content_return_url"] = "test_content_return_url"
        self.request.session["LTI_LAUNCH"]["ext_content_return_types"] = ["not_lti_launch_url"]
        response = self.client.get(reverse("resource_selection"))
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, "add_module_item.html")
    
    def test_resource_selection_view_unauthorized(self):
        """Tests add_module_item template does not renders for url 'resource_selection' when unauthorized"""
        self.set_roles([])
        response = self.client.get(reverse("resource_selection"))
        self.assertTemplateNotUsed(response, "add_module_item.html")

