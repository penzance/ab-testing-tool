from ab_tool.tests.common import (SessionTestCase, APIReturn,
    LIST_MODULES, LIST_ITEMS, TEST_COURSE_ID, TEST_OTHER_COURSE_ID)
from ab_tool.canvas import (get_lti_param, list_modules,
    list_module_items, get_canvas_request_context, CanvasModules)
from ab_tool.exceptions import (MISSING_LTI_LAUNCH, MISSING_LTI_PARAM,
    NO_SDK_RESPONSE)
from mock import patch, MagicMock
from requests.exceptions import RequestException
from django_canvas_oauth.exceptions import NewTokenNeeded
from ab_tool.controllers import intervention_point_url

class TestCanvas(SessionTestCase):
    def mock_request_exception(self):
        exception = RequestException()
        exception.response = MagicMock()
        return exception
    
    def mock_unauthorized_exception(self):
        exception = RequestException()
        exception.response = MagicMock()
        exception.response.status_code = 401
        return exception

    def get_canvas_modules(self, list_modules_return=[], list_items_return=[]):
        with patch(LIST_MODULES, return_value=APIReturn(list_modules_return)):
            with patch(LIST_ITEMS, return_value=APIReturn(list_items_return)):
                return CanvasModules(self.request)
    
    def test_get_lti_param_success(self):
        """ Tests that get_lti_param returns the correct value when it is present """
        param_val = "test_param_val"
        self.request.session["LTI_LAUNCH"]["test_param"] = param_val
        self.assertEqual(param_val, get_lti_param(self.request, "test_param"))
    
    def test_get_lti_param_failure(self):
        """ Tests that get_lti_param errors when param is not present """
        """ Tests that get_lti_param errors when param is not present """
        self.request.session["LTI_LAUNCH"] = {}
        self.assertRaisesSpecific(MISSING_LTI_PARAM, get_lti_param,
                                  self.request, "test_param")
    
    def test_get_lti_param_no_LTI_LAUNCH(self):
        """ Tests that get_lti_param errors when LTI_LAUNCH is not present """
        del self.request.session["LTI_LAUNCH"]
        self.assertRaisesSpecific(MISSING_LTI_LAUNCH, get_lti_param,
                                  self.request, "test_param")
    
    @patch(LIST_ITEMS, return_value=APIReturn(["item"]))
    def test_list_module_items_returns_normal(self, _mock):
        """ Tests that list_module_items returns the sdk response as a python
            object """
        request_context = get_canvas_request_context(self.request)
        self.assertEqual(list_module_items(request_context, TEST_COURSE_ID, 0),
                         ["item"])
    
    def test_list_module_items_error(self):
        """ Tests that list_module_items correctly catches RequestExceptions """
        request_context = get_canvas_request_context(self.request)
        with patch(LIST_ITEMS, side_effect=self.mock_request_exception()):
            self.assertRaisesSpecific(NO_SDK_RESPONSE, list_module_items,
                                      request_context, TEST_COURSE_ID, 0)
    
    def test_list_module_items_new_token_needed(self):
        """ Tests that list_module_items raises a NewTokenNeeded exception
            if canvas returns a "401:unauthorized" """
        request_context = get_canvas_request_context(self.request)
        with patch(LIST_ITEMS, side_effect=self.mock_unauthorized_exception()):
            self.assertRaises(NewTokenNeeded, list_module_items,
                              request_context, TEST_COURSE_ID, 0)
    
    @patch(LIST_MODULES, return_value=APIReturn(["item"]))
    def test_list_modules_returns_normal(self, _mock):
        """ Tests that list_modules returns the sdk response as a python
            object """
        request_context = get_canvas_request_context(self.request)
        self.assertEqual(list_modules(request_context, TEST_COURSE_ID), ["item"])
    
    def test_list_modules_error(self):
        """ Tests that list_modules correctly catches RequestExceptions """
        request_context = get_canvas_request_context(self.request)
        with patch(LIST_MODULES, side_effect=self.mock_request_exception()):
            self.assertRaisesSpecific(NO_SDK_RESPONSE, list_modules,
                                      request_context, TEST_COURSE_ID)
    
    def test_list_modules_new_token_needed(self):
        """ Tests that list_modules raises a NewTokenNeeded exception
            if canvas returns a "401:unauthorized" """
        request_context = get_canvas_request_context(self.request)
        with patch(LIST_MODULES, side_effect=self.mock_unauthorized_exception()):
            self.assertRaises(NewTokenNeeded, list_modules,
                              request_context, TEST_COURSE_ID)
    
    def test_get_uninstalled_intervention_points(self):
        """ Tests method get_uninstalled_intervention_points runs and returns no intervention_points when
            database empty """
        intervention_points = self.get_canvas_modules().get_uninstalled_intervention_points()
        self.assertEqual(len(intervention_points), 0)
    
    def test_get_uninstalled_intervention_points_with_item(self):
        """ Tests method get_uninstalled_intervention_points returns one when database has
            one item and api returns nothing """
        self.create_test_intervention_point()
        canvas_modules = self.get_canvas_modules(list_modules_return=[{"id": 0}])
        intervention_points = canvas_modules.get_uninstalled_intervention_points()
        self.assertEqual(len(intervention_points), 1)
    
    def test_get_uninstalled_intervention_points_against_courses(self):
        """ Tests method get_uninstalled_intervention_points returns one when database has
            two items but only one matches the course and api returns nothing """
        intervention_point = self.create_test_intervention_point(name="ip1")
        self.create_test_intervention_point(name="ip2", course_id=TEST_OTHER_COURSE_ID)
        canvas_modules = self.get_canvas_modules(list_modules_return=[{"id": 0}])
        intervention_points = canvas_modules.get_uninstalled_intervention_points()
        self.assertEqual(len(intervention_points), 1)
        self.assertSameIds([intervention_point], intervention_points)
    
    def test_get_uninstalled_intervention_points_with_all_installed(self):
        """ Tests method get_uninstalled_intervention_points returns zero when intervention_point in
            database is also returned by the API, which means it is installed """
        intervention_point = self.create_test_intervention_point()
        mock_item = {"type": "ExternalTool",
                     "external_url": intervention_point_url(self.request, intervention_point.id)}
        canvas_modules = self.get_canvas_modules(list_modules_return=[{"id": 0}], list_items_return=[mock_item])
        intervention_points = canvas_modules.get_uninstalled_intervention_points()
        self.assertEqual(len(intervention_points), 0)
    
    def test_get_uninstalled_intervention_points_with_some_installed(self):
        """ Tests method get_uninstalled_intervention_points returns one when there are two
            intervention_points in the database, one of which is also returned by the API,
            which means it is installed """
        intervention_point = self.create_test_intervention_point(name="ip1")
        self.create_test_intervention_point(name="ip2")
        mock_item = {"type": "ExternalTool",
                     "external_url": intervention_point_url(self.request, intervention_point.id)}
        canvas_modules = self.get_canvas_modules(list_modules_return=[{"id": 0}], list_items_return=[mock_item])
        intervention_points = canvas_modules.get_uninstalled_intervention_points()
        self.assertEqual(len(intervention_points), 1)
    
    def test_all_intervention_point_urls_empty(self):
        """ Tests that all_intervention_point_urls returns empty when there are no intervention_points """
        urls = self.get_canvas_modules()._all_intervention_point_urls()
        self.assertEqual(len(urls), 0)
    
    def test_all_intervention_point_urls_one_element(self):
        """ Tests that all_intervention_point_urls returns the url for one intervention_point when
            that is in the database """
        intervention_point = self.create_test_intervention_point()
        urls = self.get_canvas_modules()._all_intervention_point_urls()
        self.assertEqual(len(urls), 1)
        self.assertEqual({intervention_point_url(self.request, intervention_point.id): intervention_point}, urls)
    
    def test_all_intervention_point_urls_multiple_courses(self):
        """ Tests that all_intervention_point_urls only returns the url for the intervention_point
            in the database that matches the course_id """
        intervention_point = self.create_test_intervention_point(name="ip1")
        self.create_test_intervention_point(name="ip2", course_id=TEST_OTHER_COURSE_ID)
        urls = self.get_canvas_modules()._all_intervention_point_urls()
        self.assertEqual(len(urls), 1)
        self.assertEqual({intervention_point_url(self.request, intervention_point.id): intervention_point}, urls)
    
    def test_get_modules_with_items(self):
        """ Tests that get_modules_with_items returns with appropriate values """
        intervention_point = self.create_test_intervention_point(name="test_database_name")
        mock_item = {"type": "ExternalTool",
                     "external_url": intervention_point_url(self.request, intervention_point.id)}
        canvas_modules = self.get_canvas_modules(list_modules_return=[{"id": 0}], list_items_return=[mock_item])
        modules = canvas_modules.get_modules_with_items()
        module_item = modules[0]["module_items"][0]
        self.assertEqual(module_item["is_intervention_point"], True)
        self.assertEqual(module_item["database_name"], "test_database_name")
