from ab_testing_tool.pages.main_pages import ADMINS, STAGE_URL_TAG
from ab_testing_tool.canvas import InvalidResponseError, parse_response
from ab_testing_tool.tests.common import SessionTestCase

class test_selection_pages(SessionTestCase):
    """Tests related to selection pages and methods"""

