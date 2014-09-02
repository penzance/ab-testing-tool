from django.core.urlresolvers import reverse
from ab_testing_tool_app.tests.common import SessionTestCase, TEST_COURSE_ID
from ab_testing_tool_app.models import Stage
from django.template.defaultfilters import urlencode
from ab_testing_tool_app.controllers import stage_url

class test_selection_pages(SessionTestCase):
    """Tests related to selection pages and methods"""

    def test_resource_selection_view(self):
        """Tests add_module_item template renders for url 'resource_selection' when authenticated"""
        data = {"ext_content_return_types": ["lti_launch_url"],
                "ext_content_return_url": "http://test_content_return_url.com"}
        response = self.client.get(reverse("resource_selection"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("content_return_url", response.context)
        self.assertEqual(response.context["content_return_url"], "http://test_content_return_url.com")
        self.assertTemplateUsed(response, "add_module_item.html")
    
    def test_resource_selection_view_unauthorized(self):
        """Tests add_module_item template does not renders for url 'resource_selection' when unauthorized"""
        self.set_roles([])
        response = self.client.get(reverse("resource_selection"), follow=True)
        self.assertTemplateNotUsed(response, "add_module_item.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_resource_selection_view_without_ext_content_return_url(self):
        """Tests add_module_item template renders for url 'resource_selection' when authenticated"""
        data = {"ext_content_return_types": ["not_lti_launch_url"]}
        response = self.client.post(reverse("resource_selection"), data, follow=True)
        self.assertContains(response, "Error: no ext_content_return_url", status_code=401)

    def test_resource_selection_view_without_ext_content_return_types(self):
        """Tests add_module_item template renders for url 'resource_selection' when authenticated"""
        data = {"ext_content_return_types": [u"lti_launch_url"],
                "ext_content_return_url": "http://test_content_return_url.com"}
        response = self.client.post(reverse("resource_selection"), data, follow=True)
        self.assertEqual(response.status_code, 401)
        #TODO: self.assertContains(response, "Error: invalid ext_content_return_types")

    def test_submit_selection(self):
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        content_return_url = "http://test_content_return_url.com"
        data = {"stage_id": stage.id, "content_return_url": content_return_url}
        response = self.client.post(reverse("submit_selection"), data)
        params = {"return_type": "lti_launch_url",
                   "url": stage_url(self.request, stage.id),
                   "text": stage.name,
                  }
        #TODO
        #self.assertRedirects(response, "%s?%s" % (content_return_url, urlencode(params)))
        pass

    def test_submit_selection_new_stage(self):
        num_stages = Stage.objects.count()
        data = {"name": "stage", "notes": "hi"}
        response = self.client.post(reverse("submit_selection_new_stage"), data)
        self.assertEqual(num_stages + 1, Stage.objects.count())
        #TODO
        #assertRedirects(response, "%s?%s" % (content_return_url, urlencode(params)))
        pass
