from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.importlib import import_module
from json import dumps
from mock import patch, MagicMock

from ab_testing_tool.pages.main_pages import ADMINS, STAGE_URL_TAG
from ab_testing_tool.controllers import (get_uninstalled_stages,
    stage_url, get_full_host)
from ab_testing_tool.canvas import InvalidResponseError, parse_response
from ab_testing_tool.tests.test_main_pages import SessionTestCase

class test_selection_pages(SessionTestCase):
    """Tests related to selection pages and methods"""

