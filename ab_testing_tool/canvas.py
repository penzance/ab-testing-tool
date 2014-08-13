from canvas_sdk import RequestContext
from canvas_sdk.methods.modules import (list_module_items, list_modules,
      create_module_item)

from controllers import get_lti_param, parse_response

#TODO: change from secure.py setting to oauth handoff
from ab_testing_tool.settings.secure import COURSE_OAUTH_TOKEN


"""
Canvas API related methods are located in this module

"""

def get_canvas_request_context(request):
    oauth_token = COURSE_OAUTH_TOKEN
    canvas_url = "https://{0}/api".format(get_lti_param(request, "custom_canvas_api_domain"))
    return RequestContext(oauth_token, canvas_url)


def get_module_items(all_modules, request_context, course_id):
    """
    Takes all_modules dict and fetches module items for each module to be added
    to the returned dict.
    """
    for module in all_modules:
        response = list_module_items(request_context, course_id, module["id"], "content_details")
        module["module_items"] = parse_response(response)
    return all_modules
