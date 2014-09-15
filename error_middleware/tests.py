from ab_testing_tool_app.tests.common import SessionTestCase
from mock import patch
from error_middleware.middleware import (RenderableError, ErrorMiddleware,
    UNKNOWN_ERROR_STRING)
from error_middleware.exceptions import DEFAULT_ERROR_STATUS, Renderable400,\
    Renderable403, Renderable404, Renderable500
from django.template.base import TemplateDoesNotExist


class TestMiddleware(SessionTestCase):
    def test_renderable_error_has_status_code(self):
        """ Tests that a RenderableError has a status_code attribute """
        error = RenderableError()
        self.assertEqual(error.status_code, DEFAULT_ERROR_STATUS)
    
    def test_renderable_error_custom_data(self):
        """ Tests that a RenderableError can have custom message and status code """
        error = RenderableError("test_message", 418)
        self.assertEqual("test_message", str(error))
        self.assertEqual(error.status_code, 418)
    
    def test_error_middleware_passthrough(self):
        """ Tests that the ErrorMiddleware returns None on a normal Exception """
        middleware = ErrorMiddleware()
        ret = middleware.process_exception(self.request, Exception("xxx"))
        self.assertEqual(ret, None)
    
    def test_error_middleware_catches_renderable_error(self):
        """ Tests that the ErrorMiddleware returns not none on a
            RenderableError """
        middleware = ErrorMiddleware()
        resp = middleware.process_exception(self.request, RenderableError("xxx"))
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, DEFAULT_ERROR_STATUS)
    
    def test_error_middleware_catches_400(self):
        """ Tests that the ErrorMiddleware returns the correct status code for
            a Renderable400 """
        middleware = ErrorMiddleware()
        resp = middleware.process_exception(self.request, Renderable400("xxx"))
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 400)
    
    def test_error_middleware_catches_403(self):
        """ Tests that the ErrorMiddleware returns the correct status code for
            a Renderable403 """
        middleware = ErrorMiddleware()
        resp = middleware.process_exception(self.request, Renderable403("xxx"))
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 403)

    def test_error_middleware_catches_404(self):
        """ Tests that the ErrorMiddleware returns the correct status code for
            a Renderable404 """
        middleware = ErrorMiddleware()
        resp = middleware.process_exception(self.request, Renderable404("xxx"))
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 404)

    def test_error_middleware_catches_500(self):
        """ Tests that the ErrorMiddleware returns the correct status code for
            a Renderable500 """
        middleware = ErrorMiddleware()
        resp = middleware.process_exception(self.request, Renderable500("xxx"))
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 500)
    
    def test_error_middleware_custom_status(self):
        """ Tests that the ErrorMiddleware returns the correct status on a
            RenderableError """
        middleware = ErrorMiddleware()
        resp = middleware.process_exception(
                self.request, RenderableError("xxx", status_code=418))
        self.assertEqual(resp.status_code, 418)
    
    @patch("error_middleware.middleware.loader.render_to_string")
    def test_error_middleware_message(self, mock_renderer):
        """ Tests that ErrorMiddleware passes the right arguments to
            the template loader """
        message = "test_error_message"
        middleware = ErrorMiddleware()
        middleware.process_exception(self.request, RenderableError(message))
        mock_renderer.assert_called_with("error.html", {"message": message})
    
    @patch("error_middleware.middleware.loader.render_to_string")
    def test_error_middleware_no_message(self, mock_renderer):
        """ Tests that ErrorMiddleware returns the right message when the
            exception doesn't provide one """
        middleware = ErrorMiddleware()
        middleware.process_exception(self.request, RenderableError())
        mock_renderer.assert_called_with(
                "error.html",  {"message": UNKNOWN_ERROR_STRING})
    
    @patch("error_middleware.middleware.loader.render_to_string",
           side_effect=TemplateDoesNotExist)
    def test_error_middleware_no_error_template(self, mock_renderer):
        """ Tests that ErrorMiddleware still works when there is no error.html
            template present """
        message = "test_error_message"
        middleware = ErrorMiddleware()
        resp = middleware.process_exception(self.request, RenderableError(message))
        self.assertEqual(resp.status_code, DEFAULT_ERROR_STATUS)
