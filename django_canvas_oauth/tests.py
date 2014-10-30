import json
from django.test.testcases import TestCase
from django.contrib.auth.models import User
from mock import MagicMock, patch

from django_canvas_oauth.models import OAuthToken
from django_canvas_oauth.middleware import OAuthMiddleware
from django_canvas_oauth.exceptions import NewTokenNeeded, BadLTIConfigError,\
    BadOAuthReturnError
from django_canvas_oauth.oauth import get_token, begin_oauth, get_oauth_service,\
    AUTHORIZE_URL_PATTERN, oauth_callback

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
    
    def test_get_token_succuess(self):
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
        self.client
        response = begin_oauth(self.request())
        redirect_url = response._headers['location'][1]
        self.assertIn(AUTHORIZE_URL_PATTERN % self.TEST_DOMAIN, redirect_url)
    
    def test_oauth_callback_bad_params(self):
        """ Tests that oauth_callback errors on an error param or no params """
        self.assertRaises(BadOAuthReturnError, oauth_callback, self.request())
        self.assertRaises(BadOAuthReturnError, oauth_callback,
                           self.request(get_params={"error": "some_error"}))
        self.assertRaises(BadOAuthReturnError, oauth_callback,
                           self.request(get_params={"error": "x", "code": "y"}))
    
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
