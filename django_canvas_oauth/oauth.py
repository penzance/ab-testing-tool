import json
from datetime import timedelta
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.template.base import TemplateDoesNotExist
from django.template import loader
from django.utils import timezone
from rauth import OAuth2Service

from django_canvas_oauth.models import OAuthToken
from django_canvas_oauth.exceptions import (NewTokenNeeded, BadLTIConfigError)


BASE_URL_PATTERN = "https://%s/"
AUTHORIZE_URL_PATTERN = "https://%s/login/oauth2/auth"
ACCESS_TOKEN_URL_PATTERN = "https://%s/login/oauth2/token"

OAUTH_ERROR_TEMPLATE = "oauth_error.html"
if hasattr(settings, "OAUTH_ERROR_TEMPLATE"):
    OAUTH_ERROR_TEMPLATE = settings.OAUTH_ERROR_TEMPLATE


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
    if check_for_redirect_loop(request):
        return render_oauth_error(
            "It appears you don't have sufficient canvas permissions to use this " +
            "external tool for this course.  Please contact your canvas administrator."
        )
    service = get_oauth_service(request)
    redirect_uri = request.build_absolute_uri(reverse("django_canvas_oauth:oauth_page"))
    #TODO: Implement with param `state` for security. See cited documentation.
    return redirect(service.get_authorize_url(response_type="code",
                                              redirect_uri=redirect_uri))


def check_for_redirect_loop(request):
    """
    If we detect that the user generated an OAuth token in the past 30
    seconds, the user is almost certainly caught in the OAuth login loop.
    This is most likely caused by the fact that the python_canvas_sdk
    returns multiple kinds of 401 errors, including
    401: {u'errors': [{u'message': u'Invalid access token.'}]
    for which we want to generate a new token, but also
    401: {u'status': u'unauthorized', u'errors':
          [{u'message': u'user not authorized to perform that action'}]}
    which means the user deosn't have sufficient permissions in the course.
    """
    try:
        token_updated = request.user.oauthtoken.updated_on
        if timezone.now() - token_updated < timedelta(seconds=30):
            return True
    except OAuthToken.DoesNotExist:
        pass
    return False



def oauth_callback(request):
    """ Receives the callback from canvas and saves the token to the database.
        Redirects user to the page they came from at the start of the oauth
        procedure. """
    error = request.GET.get("error", None)
    if error:
        return render_oauth_error(error)
    code = request.GET.get("code", None)
    if not code:
        return render_oauth_error("No code param in oauth_middleware response")
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
    base_url = BASE_URL_PATTERN % canvas_domain
    authorize_url = AUTHORIZE_URL_PATTERN % canvas_domain
    access_token_url = ACCESS_TOKEN_URL_PATTERN % canvas_domain
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


def render_oauth_error(error_message):
    """ If there is an error in the oauth callback, attempts to render it in a
        template that can be styled; otherwise, if OAUTH_ERROR_TEMPLATE not defined,
        this will return a HttpResponse with status 403 """
    try:
        template = loader.render_to_string(OAUTH_ERROR_TEMPLATE, {"message": error_message})
    except TemplateDoesNotExist:
        return HttpResponse("Error: %s" % error_message, status=403)
    return HttpResponse(template, status=403)

