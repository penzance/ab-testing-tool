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
    
    def test_page_decorator_passthrough(self):
        """ Tests that the page decorator doesn't modify the response of a
            page not raising an exception """
        expected_response = HttpResponse("test")
        response = self.page_with_return(expected_response)
        self.assertEqual(expected_response, response)
