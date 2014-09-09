import logging
import traceback
from django.http.response import HttpResponse
from django.template import loader
from django.template.base import TemplateDoesNotExist

logger = logging.getLogger(__name__)

UNKNOWN_ERROR_STRING = "An unknown error occurred in the A/B testing tool"

class ErrorMiddleware(object):
    
    def process_exception(self, request, exception):
        logger.error(repr(exception))
        logger.error(traceback.format_exc())
        message = str(exception)
        if not message:
            message = UNKNOWN_ERROR_STRING
        try:
            template = loader.render_to_string("error.html", {"message": message})
        except TemplateDoesNotExist:
            logger.warn("No template 'error.html' found")
            return HttpResponse("Error: %s" % message, status=400)
        return HttpResponse(template, status=400)
