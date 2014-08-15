import logging
import traceback
from functools import wraps
from django.shortcuts import render_to_response
from django.http.response import HttpResponse

UNKNOWN_ERROR = "An unknown error occurred in the A/B testing tool"


def page(f):
    """ Decorator for page-view functions to handle errors; if an exception
        occurs in the wrapped view, the error template will be returned
        with the message of the exception.  If there is an error in this logic,
        a plain HttpResponse is returned. """
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return wrapped_page(f, args, kwargs)
        except Exception:
            return HttpResponse(UNKNOWN_ERROR)
    return wrapped


def wrapped_page(f, args, kwargs):
    """ This is the error handling/rendering logic for the page decorator """
    try:
        response = f(*args, **kwargs)
        return response
    except Exception as e:
        logging.error(repr(e))
        logging.error(traceback.format_exc())
        message = str(e)
        if not message:
            message = UNKNOWN_ERROR
        return render_to_response("error.html", {"message": message})




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
