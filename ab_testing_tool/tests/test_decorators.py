from django.http.response import HttpResponse

from ab_testing_tool.tests.common import SessionTestCase
from ab_testing_tool.decorators import page


class test_decorators(SessionTestCase):
    def test_page_decorator_catches_error(self):
        """ Tests that a page raising an exception renders the error template
            with the correct message """
        error_message = "This is a test error message"
        @page
        def test(request):
            raise Exception(error_message)
        
        response = test(self.request)
        self.assertTemplateUsed(response, "error.html")
        self.assertContains(response, error_message)
    
    def test_page_decorator_passthrough(self):
        """ Tests that the page decorator doesn't modify the response of a
            page not raising an exception """
        expected_response = HttpResponse("test")
        @page
        def test(request):
            return expected_response
        
        response = test(self.request)
        self.assertTemplateNotUsed(response, "error.html")
        self.assertEqual(expected_response, response)
