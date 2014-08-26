from django.http.response import HttpResponse

from ab_testing_tool_app.tests.common import SessionTestCase
from ab_testing_tool_app.decorators import page
from ab_testing_tool_app.constants import UNKNOWN_ERROR_STRING,\
    DOUBLE_ERROR_STRING
from mock import patch


class TestDecorators(SessionTestCase):
    @page
    def page_with_return(self, return_value):
        """ Function with page decorator that returns normally """
        return return_value
    
    @page
    def page_with_exception(self, exception):
        """ Function with page decorator that raises an exception """
        raise exception
    
    def test_page_decorator_catches_error(self):
        """ Tests that a page raising an exception renders the error template
            with the correct message """
        error_message = "This is a test error message"
        response = self.page_with_exception(Exception(error_message))
        self.assertContains(response, error_message)
    
    def test_page_decorator_passthrough(self):
        """ Tests that the page decorator doesn't modify the response of a
            page not raising an exception """
        expected_response = HttpResponse("test")
        response = self.page_with_return(expected_response)
        self.assertEqual(expected_response, response)
    
    def test_page_decorator_unkown_error(self):
        """ Tests that the page decorator displays an unknown error when
            the Exception raised has no message """
        response = self.page_with_exception(Exception())
        self.assertContains(response, UNKNOWN_ERROR_STRING)
    
    @patch("ab_testing_tool_app.decorators.wrapped_page", side_effect=Exception())
    def test_page_decorator_no_failure(self, _mock):
        """ Tests that the page decorator still doesn't fail if wrapped_page
            has an exception """
        not_expected_response = HttpResponse("test")
        response = self.page_with_return(not_expected_response)
        self.assertNotEqual(response, not_expected_response)
        self.assertContains(response, DOUBLE_ERROR_STRING)
