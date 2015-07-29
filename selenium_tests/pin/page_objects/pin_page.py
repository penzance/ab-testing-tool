"""
This file models some of the page objects on the Manage People Search Page.  (find_user.html)
"""
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium_tests.pin.page_objects.base_page_object import PinBasePageObject
import abc

class PinPageLocators(object):
    # List of WebElements found on Pin Page (Locators)
    # Not all HTML tags are found here, but on a need basis
    LOGIN_TYPE_XID_RADIO_BUTTON = (By.ID, "compositeAuthenticationSourceType3")
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "input[name=\"_eventId_submit\"]")


class PinLoginPageObject(PinBasePageObject):
    """
    Page Object of the Pin Login Page
    """
    __metaclass__ = abc.ABCMeta

    def is_loaded(self):
        """ determine if the page loaded by looking for a specific element on the page """
        try:
            self.find_element(*PinPageLocators.LOGIN_TYPE_XID_RADIO_BUTTON)
        except NoSuchElementException:
            return False
        return True

    def set_username(self, username):
        """ set the username """
        username_element = self.find_element(*PinPageLocators.USERNAME)
        username_element.clear()
        username_element.send_keys(username)

    def set_password(self, password):
        """ set the password """
        password_element = self.find_element(*PinPageLocators.PASSWORD)
        password_element.clear()
        password_element.send_keys(password)

    def set_login_type_xid(self):
        """ set the compositeAuthenticationSourceType3 option """
        comp_auth_source_type_element = self.find_element(*PinPageLocators.LOGIN_TYPE_XID_RADIO_BUTTON)
        comp_auth_source_type_element.click()

    def click_submit(self):
        """ click the submit button """
        submit_button = self.find_element(*PinPageLocators.SUBMIT_BUTTON)
        submit_button.click()



    @abc.abstractmethod
    def login(self, username, password):
        """
        the abstract method can be overridden for individual projects to allow
        the login to return the appropriate page object for the test. If you do override
        you will need to call supper to invoke the login
         """
        print 'base class logging in user: %s' % username
        self.set_login_type_xid()
        self.set_username(username)
        self.set_password(password)
        self.click_submit()



# '''--- This class defines methods to login to PIN Authentication--''' 
# class Login(object):

#     def __init__(self, driver):
#         self._driver = driver
#         self._driver.implicitly_wait(30)


#     def fill_username(self,driver,username): 
#             #This method will send input the login field on PIN page
#             login_id = driver.find_element_by_id("username")
#             login_id.clear()
#             login_id.send_keys(username)

#     def fill_password(self,driver, password): 
#             #This method will send the password on the PIN
#             login_password = driver.find_element_by_id("password")
#             login_password.clear()
#             login_password.send_keys(password)


#     def submitlogin(self,driver):  
#             submit = driver.find_element_by_css_selector("input[name=\"_eventId_submit\"]")
#             submit.click()

#     def switchframe(self,driver): 
#             switch_to_tool_frame = driver.switch_to.frame(driver.find_element_by_id("tool_content"))

