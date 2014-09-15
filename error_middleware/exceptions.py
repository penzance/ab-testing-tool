from django.http.response import Http404
from django.core.exceptions import SuspiciousOperation, PermissionDenied


DEFAULT_ERROR_STATUS = 400


class RenderableError(Exception):
    """
    This is the Exception child class that errors intended to be displayed
    should instantiate or descend from.
    
    Example:
        def page_view(request):
            raise RenderableError("This is the message displayed by the app")
    """
    
    status_code = DEFAULT_ERROR_STATUS
    
    def __init__(self, message="", status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super(RenderableError, self).__init__(message)


class Renderable400(RenderableError, SuspiciousOperation):
    status_code = 400

class Renderable403(RenderableError, PermissionDenied):
    status_code = 403

class Renderable404(RenderableError, Http404):
    status_code = 404

class Renderable500(RenderableError):
    status_code = 500
