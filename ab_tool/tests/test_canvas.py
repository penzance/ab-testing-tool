from ab_tool.tests.common import (SessionTestCase, APIReturn,
    LIST_MODULES, LIST_ITEMS, TEST_COURSE_ID)
from ab_tool.canvas import (get_lti_param, list_modules,
    list_module_items, get_canvas_request_context)
from ab_tool.exceptions import (MISSING_LTI_LAUNCH, MISSING_LTI_PARAM,
    NO_SDK_RESPONSE)
from mock import patch, MagicMock
from requests.exceptions import RequestException
from django_canvas_oauth.exceptions import NewTokenNeeded

class TestCanvas(SessionTestCase):
    def mock_unauthorized_exception(self):
        exception = RequestException()
        exception.response = MagicMock()
        exception.response.status_code = 401
        exception.response.reason = "Unauthorized"
        return exception
    
    def test_get_lti_param_success(self):
        """ Tests that get_lti_param returns the correct value when it is present """
        param_val = "test_param_val"
        self.request.session["LTI_LAUNCH"]["test_param"] = param_val
        self.assertEqual(param_val, get_lti_param(self.request, "test_param"))
    
    def test_get_lti_param_failure(self):
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
    
    @patch(LIST_ITEMS, side_effect=RequestException())
    def test_list_module_items_error(self, _mock):
        """ Tests that list_module_items correctly catches RequestExceptions """
        request_context = get_canvas_request_context(self.request)
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
    
    @patch(LIST_MODULES, side_effect=RequestException())
    def test_list_modules_error(self, _mock):
        """ Tests that list_modules correctly catches RequestExceptions """
        request_context = get_canvas_request_context(self.request)
        self.assertRaisesSpecific(NO_SDK_RESPONSE, list_modules,
                                  request_context, TEST_COURSE_ID)
    
    def test_list_modules_new_token_needed(self):
        """ Tests that list_modules raises a NewTokenNeeded exception
            if canvas returns a "401:unauthorized" """
        request_context = get_canvas_request_context(self.request)
        with patch(LIST_MODULES, side_effect=self.mock_unauthorized_exception()):
            self.assertRaises(NewTokenNeeded, list_modules,
                              request_context, TEST_COURSE_ID)
