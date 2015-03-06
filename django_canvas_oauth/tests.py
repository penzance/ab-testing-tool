import json
from django.test.testcases import TestCase
from django.contrib.auth.models import User
from mock import MagicMock, patch

from django_canvas_oauth.models import OAuthToken
from django_canvas_oauth.middleware import OAuthMiddleware
from django_canvas_oauth.exceptions import (NewTokenNeeded, BadLTIConfigError)
from django_canvas_oauth.oauth import (get_token, begin_oauth, get_oauth_service,
    AUTHORIZE_URL_PATTERN, oauth_callback, OAUTH_ERROR_TEMPLATE)
from django.template.base import TemplateDoesNotExist
from django.utils import timezone
from datetime import datetime

TEST_TIME = timezone.make_aware(datetime(2000, 1, 1), timezone.utc)

class TestMiddleware(TestCase):
    TEST_DOMAIN = "example.com"
    
    def request(self, lti_launch={"custom_canvas_api_domain": TEST_DOMAIN},
                get_params={}):
        request = MagicMock()
        session = {"oauth_return_uri": self.TEST_DOMAIN}
        if lti_launch:
            session["LTI_LAUNCH"] = lti_launch
        request.session = session
        request.GET = get_params
        request.user.oauthtoken.updated_on = TEST_TIME
        return request
    
    @patch("django_canvas_oauth.middleware.begin_oauth")
    def test_middleware_begins_oauth(self, mock_begin_oauth):
        """ Tests that the OAtuhMiddleware calls begin_oauth on a
            NewTokenNeeded exception"""
        middleware = OAuthMiddleware()
        request = self.request()
        middleware.process_exception(request, NewTokenNeeded())
        mock_begin_oauth.assert_called_with(request)
    
    @patch("django_canvas_oauth.middleware.begin_oauth")
    def test_middleware_generic_exception_passthrough(self, mock_begin_oauth):
        """ Tests that the OAtuhMiddleware doesn't call begin_oauth on a
            NewTokenNeeded exception and returns None """
        middleware = OAuthMiddleware()
        ret = middleware.process_exception(self.request(), Exception())
        self.assertFalse(mock_begin_oauth.called)
        self.assertEqual(None, ret)
    
    def test_get_token_raises_new_token_needed(self):
        """ Tests that get_token raises a NewTokenNeeded exception if
            there is not a token for the user """
        request = MagicMock()
        request.user = User()
        self.assertRaises(NewTokenNeeded, get_token, request)
    
    def test_get_token_success(self):
        """ Tests that get_token returns a user's token if it exists """
        request = self.request()
        request.user.oauthtoken = OAuthToken(token="test_token")
        self.assertEquals(get_token(request), "test_token")
    
    def test_get_oauth_service(self):
        """ Tests that ouath service has the correct domain in its urls """
        service = get_oauth_service(self.request())
        self.assertIn(self.TEST_DOMAIN, service.authorize_url)
        self.assertIn(self.TEST_DOMAIN, service.access_token_url)
        self.assertIn(self.TEST_DOMAIN, service.base_url)
    
    def test_get_oauth_service_bad_lti_launch(self):
        """ Tests that get_oauth_service raises a BadLTIConfigError if
            there is no LTI_LAUNCH in session or it is missing parameters """
        self.assertRaises(BadLTIConfigError, get_oauth_service,
                          self.request(None))
        self.assertRaises(BadLTIConfigError, get_oauth_service,
                          self.request({"junk": "stuff"}))
    
    def test_begin_oauth_redirect(self):
        """ Tests that begin_oauth redirects to the authorize url """
        response = begin_oauth(self.request())
        redirect_url = response._headers['location'][1]
        self.assertIn(AUTHORIZE_URL_PATTERN % self.TEST_DOMAIN, redirect_url)
    
    @patch("django.utils.timezone.now", return_value=TEST_TIME)
    @patch("error_middleware.middleware.loader.render_to_string")
    def test_oauth_loop_detection(self, mock_renderer, _mock):
        """ Tests that there is an error page for a redirect loop (if it is being
            called to generate a token just after it generated one) """
        response = begin_oauth(self.request())
        mock_renderer.assert_called_with(
                OAUTH_ERROR_TEMPLATE,
                {"message":
                    "It appears you don't have sufficient canvas permissions " +
                    "to use this external tool for this course.  " +
                    "Please contact your canvas administrator."}
        )
        self.assertEqual(response.status_code, 403)
    
    @patch("error_middleware.middleware.loader.render_to_string")
    def test_oauth_callback_fails_with_template(self, mock_renderer):
        """ Tests that an error page is displayed if there is no code param """
        response = oauth_callback(self.request())
        mock_renderer.assert_called_with(OAUTH_ERROR_TEMPLATE, {"message":
                                "No code param in oauth_middleware response"})
        self.assertEqual(response.status_code, 403)
    
    @patch("error_middleware.middleware.loader.render_to_string")
    def test_oauth_callback_fails_with_template_and_error(self, mock_renderer):
        """ Tests that an error page is displayed if the oauth_callback gets an error """
        response = oauth_callback(self.request(get_params={"error": "test_error"}))
        mock_renderer.assert_called_with(OAUTH_ERROR_TEMPLATE, {"message":
                                "test_error"})
        self.assertEqual(response.status_code, 403)
    
    @patch("error_middleware.middleware.loader.render_to_string",
           side_effect=TemplateDoesNotExist)
    def test_oauth_callback_fails_without_error_template(self, mock_renderer):
        """ Tests that an error page is displayed even if there is no error template """
        response = oauth_callback(self.request())
        self.assertContains(response, "No code param in oauth_middleware response",
                            status_code=403, html=False)
    
    @patch("django_canvas_oauth.oauth.get_oauth_service")
    def test_oauth_callback_success(self, mock_get_oauth_service):
        """ Test that oauth callback stores new token and redirects properly """
        user = User.objects.create()
        request = self.request(get_params={"code": "test_code"})
        request.user = user
        mock_service = MagicMock()
        mock_service.get_access_token.return_value = "test_token"
        mock_get_oauth_service.return_value = mock_service
        response = oauth_callback(request)
        mock_service.get_access_token.assert_called_with(
                decoder=json.loads, params={"code": "test_code"})
        self.assertEqual(response._headers['location'][1], self.TEST_DOMAIN)
        self.assertEqual(User.objects.get(pk=user.pk).oauthtoken.token, "test_token")
    
    @patch("django_canvas_oauth.oauth.get_oauth_service")
    def test_oauth_callback_success_new_token(self, mock_get_oauth_service):
        """ Test that oauth callback stores new token when user has
            an existing token """
        user = User.objects.create()
        OAuthToken.objects.create(user=user, token="old_token")
        request = self.request(get_params={"code": "test_code"})
        request.user = user
        mock_service = MagicMock()
        mock_service.get_access_token.return_value = "test_token"
        mock_get_oauth_service.return_value = mock_service
        response = oauth_callback(request)
        self.assertEqual(response._headers['location'][1], self.TEST_DOMAIN)
        self.assertEqual(User.objects.get(pk=user.pk).oauthtoken.token, "test_token")
