import json
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from rauth import OAuth2Service

from django_canvas_oauth.models import OAuthToken
from django_canvas_oauth.exceptions import (NewTokenNeeded, BadLTIConfigError,
    BadOAuthReturnError)


def get_token(request):
    """ Retrieves a token for the user if one exists already.
        If there isn't one, it raises a NewTokenNeeded exception.  If this
        happens inside a view, this exception will be handled by the
        django_canvas_oauth middleware to call begin_oauth.  If this
        happens outside of a view, then there is no token available for
        that user and they must be directed to the site to authorize a token."""
    try:
        return request.user.oauthtoken.token
    except OAuthToken.DoesNotExist:
        """ If this exception is raised by a view function and not caught,
        it is probably because the oauth_middleware is not installed, since it
        is supposed to catch this error."""
        raise NewTokenNeeded("No token found for that admin_id and course_id")


def begin_oauth(request):
    """ Redirects user to canvas with a request for token.  Stores where the
        user came from so they can be redirected back there at the end.
        https://canvas.instructure.com/doc/api/file.oauth.html """
    request.session["oauth_return_uri"] = request.get_full_path()
    service = get_oauth_service(request)
    redirect_uri = request.build_absolute_uri(reverse("django_canvas_oauth:oauth_page"))
    #TODO: Implement with param `state` for security. See cited documentation.
    return redirect(service.get_authorize_url(response_type="code",
                                              redirect_uri=redirect_uri))


def oauth_callback(request):
    """ Receives the callback from canvas and saves the token to the database.
        Redirects user to the page they came from at the start of the oauth
        procedure. """
    error = request.GET.get("error", None)
    if error:
        raise BadOAuthReturnError("%s" % error)
    code = request.GET.get("code", None)
    if not code:
        raise BadOAuthReturnError("No code param in oauth_middleware response")
    service = get_oauth_service(request)
    token = service.get_access_token(decoder=json.loads, params={"code": code})
    o_auth_token, created = OAuthToken.objects.get_or_create(
                user=request.user, defaults={"token": token})
    if not created:
        # Replace existing token if one exists
        o_auth_token.token = token
        o_auth_token.save()
    return redirect(request.session["oauth_return_uri"])


def get_oauth_service(request):
    """ Gets the rauth oauth2 service to handle this request """
    canvas_domain = get_lti_param(request, "custom_canvas_api_domain")
    base_url = "https://%s/" % canvas_domain
    authorize_url = "https://%s/login/oauth2/auth" % canvas_domain
    access_token_url = "https://%s/login/oauth2/token" % canvas_domain
    return OAuth2Service(client_id=settings.CANVAS_OAUTH_CLIENT_ID,
                         client_secret=settings.CANVAS_OAUTH_CLIENT_SECRET,
                         name="canvas",
                         authorize_url=authorize_url,
                         access_token_url=access_token_url,
                         base_url=base_url)


def get_lti_param(request, key):
    """ Note: Copy of function in ab_testing_tool_app.canvas.py """
    if "LTI_LAUNCH" not in request.session:
        raise BadLTIConfigError("LTI_LAUNCH not in session")
    if key not in request.session["LTI_LAUNCH"]:
        raise BadLTIConfigError("Missing LTI parameter in session")
    return request.session["LTI_LAUNCH"][key]