import logging
import traceback
from django.conf import settings
from django.http.response import HttpResponse
from django.template import loader
from django.template.base import TemplateDoesNotExist
from error_middleware.exceptions import RenderableError

logger = logging.getLogger(__name__)

""" String used for error message when a RenderableError is raised with no
    message; can be changed with Django setting UNKNOWN_ERROR_STRING """
UNKNOWN_ERROR_STRING = "An unknown error occurred"
if hasattr(settings, "UNKNOWN_ERROR_STRING"):
    UNKNOWN_ERROR_STRING = settings.UNKNOWN_ERROR_STRING

""" Template to render to display RenderableErorrs; can be changed with
    Django setting RENDERABLE_ERROR_TEMPLATE """
ERROR_TEMPLATE = "renderable_error.html"
if hasattr(settings, "RENDERABLE_ERROR_TEMPLATE"):
    ERROR_TEMPLATE = settings.RENDERABLE_ERROR_TEMPLATE

class ErrorMiddleware(object):
    """
    This middleware is to display custom errors raised in the application.
    If a RenderableError is raised by a view with this middleware installed,
    instead of a 500 page, the page returns a page with the message and status
    code of the exception (status code defaults to DEFAULT_ERROR_STATUS).
    
    In order to customize the formatting of this page, simply define a template
    called 'renderable_error.html'; if this template exists, the middleware
    passes the error message do it under template varialbe 'message'.
    """
    
    def process_exception(self, request, exception):
        if not isinstance(exception, RenderableError):
            return
        status = exception.status_code
        logger.error(repr(exception))
        logger.error(traceback.format_exc())
        message = str(exception)
        if not message:
            message = UNKNOWN_ERROR_STRING
        try:
            template = loader.render_to_string(ERROR_TEMPLATE, {"message": message})
        except TemplateDoesNotExist:
            logger.warn("No template '%s' found" % ERROR_TEMPLATE)
            return HttpResponse("Error: %s" % message, status=status)
        return HttpResponse(template, status=status)
