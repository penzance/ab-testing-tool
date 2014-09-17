from mock import patch, MagicMock
from django.template.base import TemplateDoesNotExist
from django.test.testcases import TestCase

from error_middleware.middleware import (RenderableError, ErrorMiddleware,
    UNKNOWN_ERROR_STRING, ERROR_TEMPLATE)
from error_middleware.exceptions import (DEFAULT_ERROR_STATUS, Renderable400,
    Renderable403, Renderable404, Renderable500)


class TestMiddleware(TestCase):
    def renderable_error_test(self, renderable_exception, status_code):
        middleware = ErrorMiddleware()
        resp = middleware.process_exception(MagicMock(), renderable_exception)
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, status_code)
    
    def test_renderable_error_has_status_code(self):
        """ Tests that a RenderableError has a status_code attribute """
        error = RenderableError()
        self.assertEqual(error.status_code, DEFAULT_ERROR_STATUS)
    
    def test_renderable_error_custom_data(self):
        """ Tests that a RenderableError can have custom message and status code """
        error = RenderableError("test_message")
        self.assertEqual("test_message", str(error))
        self.assertEqual(error.status_code, DEFAULT_ERROR_STATUS)
    
    def test_error_middleware_passthrough(self):
        """ Tests that the ErrorMiddleware returns None on a normal Exception """
        middleware = ErrorMiddleware()
        ret = middleware.process_exception(MagicMock(), Exception("xxx"))
        self.assertEqual(ret, None)
    
    def test_error_middleware_catches_renderable_error(self):
        """ Tests that the ErrorMiddleware returns not none on a
            RenderableError """
        self.renderable_error_test(RenderableError("xxx"), DEFAULT_ERROR_STATUS)
    
    def test_error_middleware_catches_400(self):
        """ Tests that the ErrorMiddleware returns the correct status code for
            a Renderable400 """
        self.renderable_error_test(Renderable400("xxx"), 400)
    
    def test_error_middleware_catches_403(self):
        """ Tests that the ErrorMiddleware returns the correct status code for
            a Renderable403 """
        self.renderable_error_test(Renderable403("xxx"), 403)
    
    def test_error_middleware_catches_404(self):
        """ Tests that the ErrorMiddleware returns the correct status code for
            a Renderable404 """
        self.renderable_error_test(Renderable404("xxx"), 404)
    
    def test_error_middleware_catches_500(self):
        """ Tests that the ErrorMiddleware returns the correct status code for
            a Renderable500 """
        self.renderable_error_test(Renderable500("xxx"), 500)
    
    def test_error_middleware_custom_status(self):
        """ Tests that the ErrorMiddleware returns the correct status on a
            RenderableError """
        class Renderable418(RenderableError):
            status_code = 418
        self.renderable_error_test(Renderable418("xxx"), 418)
    
    @patch("error_middleware.middleware.loader.render_to_string")
    def test_error_middleware_message(self, mock_renderer):
        """ Tests that ErrorMiddleware passes the right arguments to
            the template loader """
        message = "test_error_message"
        middleware = ErrorMiddleware()
        middleware.process_exception(MagicMock(), RenderableError(message))
        mock_renderer.assert_called_with(ERROR_TEMPLATE, {"message": message})
    
    @patch("error_middleware.middleware.loader.render_to_string")
    def test_error_middleware_no_message(self, mock_renderer):
        """ Tests that ErrorMiddleware returns the right message when the
            exception doesn't provide one """
        middleware = ErrorMiddleware()
        middleware.process_exception(MagicMock(), RenderableError())
        mock_renderer.assert_called_with(
                ERROR_TEMPLATE,  {"message": UNKNOWN_ERROR_STRING})
    
    @patch("error_middleware.middleware.loader.render_to_string",
           side_effect=TemplateDoesNotExist)
    def test_error_middleware_no_error_template(self, mock_renderer):
        """ Tests that ErrorMiddleware still works when ERROR_TEMPALTE isn't
            present """
        message = "test_error_message"
        middleware = ErrorMiddleware()
        resp = middleware.process_exception(MagicMock(), RenderableError(message))
        self.assertEqual(resp.status_code, DEFAULT_ERROR_STATUS)
