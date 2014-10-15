from mock import patch, MagicMock

from ab_tool.controllers import (get_uninstalled_intervention_points, intervention_point_url,
    all_intervention_point_urls, format_url, post_param)
from ab_tool.tests.common import (SessionTestCase, APIReturn,
    LIST_MODULES, LIST_ITEMS, TEST_COURSE_ID, TEST_OTHER_COURSE_ID)
from ab_tool.models import InterventionPoint
from ab_tool.exceptions import BAD_STAGE_ID


class TestControllers(SessionTestCase):
    def test_get_uninstalled_intervention_points(self):
        """ Tests method get_uninstalled_intervention_points runs and returns no intervention_points when
            database empty """
        intervention_points = get_uninstalled_intervention_points(self.request)
        self.assertEqual(len(intervention_points), 0)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_intervention_points_with_item(self, _mock1):
        """ Tests method get_uninstalled_intervention_points returns one when database has
            one item and api returns nothing """
        self.create_test_intervention_point()
        intervention_points = get_uninstalled_intervention_points(self.request)
        self.assertEqual(len(intervention_points), 1)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_intervention_points_against_courses(self, _mock1):
        """ Tests method get_uninstalled_intervention_points returns one when database has
            two items but only one matches the course and api returns nothing """
        intervention_point = self.create_test_intervention_point(name="ip1")
        self.create_test_intervention_point(name="ip2", course_id=TEST_OTHER_COURSE_ID)
        intervention_points = get_uninstalled_intervention_points(self.request)
        self.assertEqual(len(intervention_points), 1)
        self.assertSameIds([intervention_point], intervention_points)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_intervention_points_with_all_installed(self, _mock1):
        """ Tests method get_uninstalled_intervention_points returns zero when intervention_point in
            database is also returned by the API, which means it is installed """
        intervention_point = self.create_test_intervention_point()
        mock_item = {"type": "ExternalTool",
                     "external_url": intervention_point_url(self.request, intervention_point.id)}
        with patch(LIST_ITEMS, return_value=APIReturn([mock_item])):
            intervention_points = get_uninstalled_intervention_points(self.request)
            self.assertEqual(len(intervention_points), 0)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_intervention_points_with_some_installed(self, _mock1):
        """ Tests method get_uninstalled_intervention_points returns one when there are two
            intervention_points in the database, one of which is also returned by the API,
            which means it is installed """
        intervention_point = self.create_test_intervention_point(name="ip1")
        self.create_test_intervention_point(name="ip2")
        mock_item = {"type": "ExternalTool",
                     "external_url": intervention_point_url(self.request, intervention_point.id)}
        with patch(LIST_ITEMS, return_value=APIReturn([mock_item])):
            intervention_points = get_uninstalled_intervention_points(self.request)
            self.assertEqual(len(intervention_points), 1)
    
    def test_all_intervention_point_urls_empty(self):
        """ Tests that all_intervention_point_urls returns empty when there are no intervention_points """
        urls = all_intervention_point_urls(self.request, TEST_COURSE_ID)
        self.assertEqual(len(urls), 0)
    
    def test_all_intervention_point_urls_one_element(self):
        """ Tests that all_intervention_point_urls returns the url for one intervention_point when
            that is in the database """
        intervention_point = self.create_test_intervention_point()
        urls = all_intervention_point_urls(self.request, TEST_COURSE_ID)
        self.assertEqual(len(urls), 1)
        self.assertEqual([intervention_point_url(self.request, intervention_point.id)], urls)
    
    def test_all_intervention_point_urls_multiple_courses(self):
        """ Tests that all_intervention_point_urls only returns the url for the intervention_point
            in the database that matches the course_id """
        intervention_point = self.create_test_intervention_point(name="ip1")
        self.create_test_intervention_point(name="ip2", course_id=TEST_OTHER_COURSE_ID)
        urls = all_intervention_point_urls(self.request, TEST_COURSE_ID)
        self.assertEqual(len(urls), 1)
        self.assertEqual([intervention_point_url(self.request, intervention_point.id)], urls)
    
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
