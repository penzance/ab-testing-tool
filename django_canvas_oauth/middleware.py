from django_canvas_oauth.exceptions import NewTokenNeeded
from django_canvas_oauth.oauth import begin_oauth


class OAuthMiddleware(object):
    """
    This middleware is to catch NewTokenNeeded errors, as is raised by the
    get_token function if there is no cached token for the user, or as should
    be raised by SDK calls if they detect the token is invalid.
    
    On catching a NewTokenNeeded error, this begins the oauth dance with canvas
    to get a new token.
    
    This middleware requires CLIENT_ID, CLIENT_SECRET to be defined in
    ab_testing_tool/settings/secure.py
    """
    
    def process_exception(self, request, exception):
        if not isinstance(exception, NewTokenNeeded):
            return
        return begin_oauth(request)