from ab_testing_tool_app.tests.common import SessionTestCase, APIReturn
from ab_testing_tool_app.canvas import get_lti_param, parse_response
from ab_testing_tool_app.exceptions import (MISSING_LTI_LAUNCH, MISSING_LTI_PARAM,
    NO_SDK_RESPONSE, INVALID_SDK_RESPONSE)
from ab_testing_tool_app.exceptions import InvalidResponseError

class test_canvas_pages(SessionTestCase):
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
    
    def test_parse_response_success(self):
        """ Tests that parse_response correctly parses an api return """
        obj = ["test object"]
        response = APIReturn(obj)
        self.assertEqual(obj, parse_response(response))
    
    def test_parse_response_not_ok(self):
        """ Tests that parse response errors when return is not 'ok' """
        obj = ["test object"]
        response = APIReturn(obj)
        response.ok = False
        self.assertRaisesSpecific(NO_SDK_RESPONSE, parse_response, response)
    
    def test_parse_response_bad_json(self):
        """ Tests that parse response errors when it has invalid json text """
        response = APIReturn(None)
        response.text = None
        self.assertRaisesSpecific(INVALID_SDK_RESPONSE, parse_response, response)
        response.text = "This is not json {}"
        self.assertRaisesSpecific(INVALID_SDK_RESPONSE, parse_response, response)
    
    def test_parse_response_error_type(self):
        """ Tests that a not OK API response raises an InvalidResponseError """
        response = APIReturn([])
        response.ok = False
        self.assertRaises(InvalidResponseError, parse_response, response)
    
    def test_parse_response_with_dict(self):
        """ Tests that an OK API response is correctly returned with a dict """
        json_obj = [{"id": 0}]
        response = APIReturn(json_obj)
        response.ok = True
        self.assertEquals(parse_response(response), json_obj)
