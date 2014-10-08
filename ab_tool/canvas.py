import logging
import traceback
from canvas_sdk.methods import modules
from canvas_sdk import RequestContext
from django.conf import settings

from ab_tool.exceptions import (MISSING_LTI_PARAM, MISSING_LTI_LAUNCH,
    NO_SDK_RESPONSE)
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

"""
Canvas API related methods are located in this module
"""

def list_module_items(request_context, course_id, module_id):
    try:
        return modules.list_module_items(request_context, course_id, module_id,
                                         "content_details").json()
    except RequestException as exception:
        logger.error(repr(exception))
        logger.error(traceback.format_exc())
        raise NO_SDK_RESPONSE

def list_modules(request_context, course_id):
    try:
        return modules.list_modules(request_context, course_id,
                                    "content_details").json()
    except RequestException as exception:
        logger.error(repr(exception))
        logger.error(traceback.format_exc())
        raise NO_SDK_RESPONSE

def get_lti_param(request, key):
    """
    Note: Not Canvas related, but located here to avoid cyclic imports
    TODO: Add this function to Django auth lti library
    """
    if "LTI_LAUNCH" not in request.session:
        raise MISSING_LTI_LAUNCH
    if key not in request.session["LTI_LAUNCH"]:
        raise MISSING_LTI_PARAM
    return request.session["LTI_LAUNCH"][key]


def get_canvas_request_context(request):
    #TODO: change from secure.py setting to oauth handoff
    oauth_token = settings.SECURE_SETTINGS["COURSE_OAUTH_TOKEN"]
    canvas_domain = get_lti_param(request, "custom_canvas_api_domain")
    canvas_url = "https://{0}/api".format(canvas_domain)
    return RequestContext(oauth_token, canvas_url)
