import logging
import traceback
from django.http.response import HttpResponse
from django.template import loader
from django.template.base import TemplateDoesNotExist

logger = logging.getLogger(__name__)

UNKNOWN_ERROR_STRING = "An unknown error occurred in the A/B testing tool"

DEFAULT_ERROR_STATUS = 400


class UserDisplayError(Exception):
    status_code = DEFAULT_ERROR_STATUS
    
    def __init__(self, message="", status_code=DEFAULT_ERROR_STATUS):
        self.status_code = status_code
        super(UserDisplayError, self).__init__(message)


class ErrorMiddleware(object):
    
    def process_exception(self, request, exception):
        if not isinstance(exception, UserDisplayError):
            return
        status = exception.status_code
        logger.error(repr(exception))
        logger.error(traceback.format_exc())
        message = str(exception)
        if not message:
            message = UNKNOWN_ERROR_STRING
        try:
            template = loader.render_to_string("error.html", {"message": message})
        except TemplateDoesNotExist:
            logger.warn("No template 'error.html' found")
            return HttpResponse("Error: %s" % message, status=status)
        return HttpResponse(template, status=status)
