from ab_testing_tool_app.tests.common import (SessionTestCase, APIReturn,
    LIST_MODULES, LIST_ITEMS, TEST_COURSE_ID)
from ab_testing_tool_app.canvas import (get_lti_param, list_modules,
    list_module_items, get_canvas_request_context)
from ab_testing_tool_app.exceptions import (MISSING_LTI_LAUNCH, MISSING_LTI_PARAM,
    NO_SDK_RESPONSE)
from mock import patch
from requests.exceptions import RequestException

class TestCanvas(SessionTestCase):
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