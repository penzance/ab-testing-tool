from django.core.urlresolvers import reverse
from ab_testing_tool.tests.common import SessionTestCase

class test_selection_pages(SessionTestCase):
    """Tests related to selection pages and methods"""

    def test_resource_selection_view(self):
        #TODO: check ext_content_return_types,content_return_url, content_return_url, stages, tracks, HttpResponse Errors
        """Tests add_module_item template renders for url 'resource_selection' when authenticated"""
        data = {"ext_content_return_types": ["not_lti_launch_url"],
                "ext_content_return_url": "http://test_content_return_url.com"}
        response = self.client.post(reverse("resource_selection"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "add_module_item.html")
    
    def test_resource_selection_view_unauthorized(self):
        """Tests add_module_item template does not renders for url 'resource_selection' when unauthorized"""
        self.set_roles([])
        response = self.client.get(reverse("resource_selection"))
        self.assertTemplateNotUsed(response, "add_module_item.html")
    
    def test_resource_selection_view_without_ext_content_return_url(self):
        #TODO: check ext_content_return_types,content_return_url, content_return_url, stages, tracks, HttpResponse Errors
        """Tests add_module_item template renders for url 'resource_selection' when authenticated"""
        data = {"ext_content_return_types": ["not_lti_launch_url"]}
        response = self.client.post(reverse("resource_selection"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Error: no ext_content_return_url")

    def test_resource_selection_view_without_ext_content_return_types(self):
        #TODO: check ext_content_return_types,content_return_url, content_return_url, stages, tracks, HttpResponse Errors
        """Tests add_module_item template renders for url 'resource_selection' when authenticated"""
        data = {"ext_content_return_types": [u"lti_launch_url"],
                "ext_content_return_url": "http://test_content_return_url.com"}
        response = self.client.post(reverse("resource_selection"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        #TODO: self.assertContains(response, "Error: invalid ext_content_return_types")

    def test_submit_selection(self):
        #assertRedirects(response, "%s?%s" % (content_return_url, urlencode(params)))
        pass

    def test_submit_selection_new_stage(self):
        #assertRedirects(response, "%s?%s" % (content_return_url, urlencode(params)))
        pass
