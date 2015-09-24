from django.conf import settings

from selenium_tests.base_test_case import BaseSeleniumTestCase
from selenium_tests.ab_tool.page_objects.pin_page import LoginPage


class ABBaseTestCase(BaseSeleniumTestCase):
    """
    Bulk Create base test case, all other tests will subclass this class
    """

    @classmethod
    def setUpClass(cls):
        """
        setup values for the tests
        """
        super(ABBaseTestCase, cls).setUpClass()
        driver = cls.driver
        cls.USERNAME = settings.SELENIUM_CONFIG.get('selenium_username')
        cls.PASSWORD = settings.SELENIUM_CONFIG.get('selenium_password')
        cls.BASE_URL = '%s/courses/5992/external_tools/1762' % settings.SELENIUM_CONFIG.get('base_url')

        #instantiate, then login to URL with username and password from settings, if running locally.
        base_login = LoginPage(driver) # instantiate
        base_login.get(cls.BASE_URL)
        base_login.login(cls.USERNAME, cls.PASSWORD)


