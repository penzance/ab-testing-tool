from mock import MagicMock

from ab_tool.controllers import (intervention_point_url, format_url, post_param)
from ab_tool.tests.common import SessionTestCase
from ab_tool.exceptions import BAD_STAGE_ID


class TestControllers(SessionTestCase):
    
    def test_intervention_point_url_contains_intervention_point_id(self):
        """ Tests that intervention_point_url contains the string of the intervention_point_id """
        intervention_point_id = 999888777
        url = intervention_point_url(self.request, intervention_point_id)
        self.assertIn(str(intervention_point_id), url)
    
    def test_intervention_point_url_works_with_string_id(self):
        """ Tests that intervention_point_url succeeds when intervention_point_id is a number string """
        intervention_point_id = "999888777"
        url = intervention_point_url(self.request, intervention_point_id)
        self.assertIn(intervention_point_id, url)
    
    def test_intervention_point_url_contains_host(self):
        """ Tests that intervention_point_url's output contains the host of the request """
        intervention_point_id = "1"
        url = intervention_point_url(self.request, intervention_point_id)
        self.assertIn(self.request.get_host(), url)
    
    def test_intervention_point_url_errors(self):
        """ Tests that intervention_point_url errors when passed a non-numeral intervention_point_id """
        self.assertRaisesSpecific(BAD_STAGE_ID, intervention_point_url, self.request, None)
        self.assertRaisesSpecific(BAD_STAGE_ID, intervention_point_url, self.request, "str")
    
    def test_format_url_passthrough(self):
        """ Tests that format_url doesn't change a proper http:// url """
        url = "http://example.com/http_stuff?thing=other_thing"
        self.assertEqual(url, format_url(url))
    
    def test_format_url_https_passthrough(self):
        """ Tests that format_url doesn't change a proper https:// url """
        url = "https://example.com/http_stuff?thing=other_thing"
        self.assertEqual(url, format_url(url))
    
    def test_format_url_adds_http(self):
        """ Tests that format_url adds http:// to a url missing it """
        url = "www.example.com/http_stuff?thing=other_thing"
        self.assertEqual("http://" + url, format_url(url))
    
    def test_post_param_success(self):
        """ Test that post_param returns correct value when param is present """
        request = MagicMock()
        request.POST = {"param_name": "param_value"}
        self.assertEqual(post_param(request, "param_name"), "param_value")
    
    def test_post_param_error(self):
        """ Test that post_param errors when requested param is missing """
        request = MagicMock()
        request.POST = {}
        self.assertRaises(Exception, post_param, request, "param_name")
