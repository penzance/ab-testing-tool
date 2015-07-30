
from selenium import webdriver
from selenium_tests.base_page_object import BasePageObject
from selenium_tests.ab_tool.page_objects.pin_page import LoginPage
from selenium_tests.base_test_case import BaseSeleniumTestCase
from django.conf import settings

from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException

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
        cls.BASE_URL = '%s/courses/5992/external_tools/1559' % settings.SELENIUM_CONFIG.get('base_url')
        # Full URL: 'https://canvas.icommons.harvard.edu/courses/5992/external_tools/1559'

        #instantiate, then login to URL with username and password from settings, if running locally.
        base_login = LoginPage(driver) # instantiating 
        base_login.get(cls.BASE_URL)
        pin_login = base_login.login(cls.USERNAME, cls.PASSWORD) 


    @classmethod
    def tearDownClass(cls):
        super(ABBaseTestCase, cls).tearDownClass()

