import logging
import traceback
from functools import wraps
from django.shortcuts import render_to_response
from django.http.response import HttpResponse
from ab_testing_tool_app.constants import UNKNOWN_ERROR_STRING,\
    DOUBLE_ERROR_STRING

logger = logging.getLogger(__name__)

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
            return HttpResponse(DOUBLE_ERROR_STRING)
    return wrapped


def wrapped_page(f, args, kwargs):
    """ This is the error handling/rendering logic for the page decorator """
    try:
        response = f(*args, **kwargs)
        return response
    except Exception as e:
        logger.error(repr(e))
        logger.error(traceback.format_exc())
        message = str(e)
        if not message:
            message = UNKNOWN_ERROR_STRING
        return render_to_response("error.html", {"message": message})
