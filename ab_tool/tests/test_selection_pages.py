from django.core.urlresolvers import reverse
from ab_tool.tests.common import (SessionTestCase, TEST_DOMAIN,
    NONEXISTENT_STAGE_ID)
from ab_tool.models import InterventionPoint, InterventionPointUrl
from django.utils.http import urlencode
from ab_tool.controllers import intervention_point_url
from mock import patch
from ab_tool.exceptions import (MISSING_RETURN_TYPES_PARAM,
    MISSING_RETURN_URL, missing_param_error)
from ab_tool.constants import STAGE_URL_TAG

class TestSelectionPages(SessionTestCase):
    """ Tests related to selection pages and methods """
    
    def test_resource_selection_view(self):
        """ Tests add_module_item template renders for url
            'resource_selection' when authenticated """
        data = {"ext_content_return_types": ["lti_launch_url"],
                "ext_content_return_url": "http://test_content_return_url.com"}
        response = self.client.post(reverse("ab:resource_selection"), data, follow=True)
        self.assertOkay(response)
        self.assertIn("content_return_url", response.context)
        self.assertEqual(response.context["content_return_url"],
                         "http://test_content_return_url.com")
        self.assertTemplateUsed(response, "ab_tool/add_module_item.html")
    
    def test_resource_selection_view_unauthorized(self):
        """ Tests add_module_item template does not render for url
            'resource_selection' when unauthorized """
        self.set_roles([])
        response = self.client.post(reverse("ab:resource_selection"), follow=True)
        self.assertTemplateNotUsed(response, "ab_tool/add_module_item.html")
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_resource_selection_view_without_ext_content_return_url(self):
        """ Test that an error is raised when there is no ext_content_return_url """
        data = {"ext_content_return_types": ["lti_launch_url"]}
        response = self.client.post(reverse("ab:resource_selection"), data, follow=True)
        self.assertError(response, MISSING_RETURN_URL)
    
    def test_resource_selection_view_missing_ext_content_return_types(self):
        """ Tests that an error is returned when there are no
            ext_content_return_types passed """
        data = {}
        response = self.client.post(reverse("ab:resource_selection"), data, follow=True)
        self.assertError(response, MISSING_RETURN_TYPES_PARAM)
    
    def test_resource_selection_view_bad_ext_content_return_types(self):
        """ Tests that an error is returned when there are unexpected
            ext_content_return_types passed """
        data = {"ext_content_return_types": ["not_lti_launch_url"]}
        response = self.client.post(reverse("ab:resource_selection"), data, follow=True)
        self.assertError(response, MISSING_RETURN_TYPES_PARAM)
    
    def test_submit_selection_with_missig_param(self):
        """ Tests that submit_selection returns an error when missing a post param """
        response = self.client.post(reverse("ab:submit_selection"), {})
        self.assertError(response, missing_param_error("intervention_point_id"))
    
    @patch("django.http.request.HttpRequest.get_host", return_value=TEST_DOMAIN)
    def test_submit_selection_with_invalid_intervention_point(self, _mock):
        """ Tests that submit_selection returns a redirect url with the
            described parameters """
        content_return_url = "http://test_content_return_url.com"
        data = {"intervention_point_id": NONEXISTENT_STAGE_ID, "content_return_url": content_return_url}
        response = self.client.post(reverse("ab:submit_selection"), data)
        self.assertEquals(response.status_code, 404)
   
    @patch("django.http.request.HttpRequest.get_host", return_value=TEST_DOMAIN)
    def test_submit_selection(self, _mock):
        """ Tests that submit_selection returns a redirect url with the
            described parameters """
        intervention_point = self.create_test_intervention_point()
        content_return_url = "http://test_content_return_url.com"
        data = {"intervention_point_id": intervention_point.id, "content_return_url": content_return_url}
        response = self.client.post(reverse("ab:submit_selection"), data)
        self.request.is_secure.return_value = False
        params = {"return_type": "lti_launch_url",
                   "url": intervention_point_url(self.request, intervention_point.id),
                   "text": intervention_point.name,
                  }
        for k, v in params.items():
            self.assertTrue(urlencode({k: v}) in response.url, urlencode({k: v}))
    
#     @patch("django.http.request.HttpRequest.get_host", return_value=TEST_DOMAIN)
#     def test_submit_selection_new_intervention_point(self, _mock):
#        #TODO: test commented due to currently disabled feature
#         """ Tests that submit_selection_new_intervention_point creates a intervention_point object and
#             returns a redirect url with the described parameters """
#         intervention_point_name = "this_is_a_intervention_point"
#         num_intervention_points = InterventionPoint.objects.count()
#         content_return_url = "http://test_content_return_url.com"
#         data = {"name": intervention_point_name, "notes": "hi",
#                 "content_return_url": content_return_url}
#         response = self.client.post(reverse("ab:submit_selection_new_intervention_point"), data)
#         self.assertEqual(num_intervention_points + 1, InterventionPoint.objects.count())
#         intervention_point = InterventionPoint.objects.get(name=intervention_point_name)
#         self.request.is_secure.return_value = False
#         params = {"return_type": "lti_launch_url",
#                    "url": intervention_point_url(self.request, intervention_point.id),
#                    "text": intervention_point_name,
#                   }
#         for k, v in params.items():
#             self.assertTrue(urlencode({k: v}) in response.url, urlencode({k: v}))
#
#     @patch("django.http.request.HttpRequest.get_host", return_value=TEST_DOMAIN)
#     def test_submit_selection_new_intervention_point_with_intervention_pointurls(self, _mock):
#        #TODO: test commented due to currently disabled feature
#         """ Tests that submit_selection_new_intervention_point creates a intervention_point object and
#         intervention_point url objects"""
#         intervention_point_name = "this_is_a_intervention_point"
#         num_intervention_points = InterventionPoint.objects.count()
#         num_intervention_pointurls = InterventionPointUrl.objects.count()
#         track1 = self.create_test_track(name="track1")
#         track2 = self.create_test_track(name="track2")
#         content_return_url = "http://test_content_return_url.com"
#         data = {"name": intervention_point_name, STAGE_URL_TAG + "1": "http://example.com/page",
#                 STAGE_URL_TAG + "2": "http://example.com/otherpage", "notes": "hi",
#                 "content_return_url": content_return_url}
#         self.client.post(reverse("ab:submit_selection_new_intervention_point"), data)
#         self.assertEqual(num_intervention_points + 1, InterventionPoint.objects.count())
#         self.assertEqual(num_intervention_pointurls + 2, InterventionPointUrl.objects.count())
#         intervention_point = InterventionPoint.objects.get(name=intervention_point_name)
#         self.assertIsNotNone(InterventionPointUrl.objects.get(intervention_point=intervention_point.id, track=track1.id))
#         self.assertIsNotNone(InterventionPointUrl.objects.get(intervention_point=intervention_point.id, track=track2.id))
