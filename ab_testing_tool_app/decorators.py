import logging
import traceback
from functools import wraps
from django.http.response import HttpResponse
from django.template import loader

UNKNOWN_ERROR = "An unknown error occurred in the A/B testing tool"

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
            logger.error(traceback.format_exc())
            return HttpResponse(UNKNOWN_ERROR, status=500)
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
            message = UNKNOWN_ERROR
        template = loader.render_to_string("error.html", {"message": message})
        return HttpResponse(template, status=400)
