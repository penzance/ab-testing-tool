# Install the A/B Testing Tool in a course



import pdb

from settings import USERS, USERNAME, PASSWORD, canvas_environment, canvas_base_url, tool_server
from selenium import webdriver

pin_login_url = "https://www.pin1.harvard.edu/cas/login?service=https%3A%2F%2F" + canvas_environment + "%2Flogin%2Fcas"

tool_config_url = tool_server + "/lti/tool_config"

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

# to run on Jenkins
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestCourseLogin(unittest.TestCase):
    # setUp to run locally
    """
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = canvas_base_url
        self.verificationErrors = []
        self.accept_next_alert = True
    """

    # setUp to run on Jenkins
    def setUp(self):
        self.driver = webdriver.Remote(
           command_executor='http://127.0.0.1:5555/wd/hub',
           desired_capabilities=DesiredCapabilities.FIREFOX)
        self.driver.implicitly_wait(10)
        self.base_url = canvas_base_url
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True    

    def test_course_login(self):
        driver = self.driver
            
        # log in to PIN
        driver.get(pin_login_url)

        time.sleep(10)

        # select the XID authentication type
        driver.find_element_by_id("compositeAuthenticationSourceType4").click()

        # log in
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys(USERNAME)
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(PASSWORD)
        driver.find_element_by_name("_eventId_submit").click()


        # go to the Selenium test course
        driver.get(self.base_url + 'settings#tab-tools')

        # Add A/B Testing Tool to the course
        driver.find_element_by_xpath("//div[@id='external_tools']/h2/button[3]").click()
        driver.find_element_by_id("external_tool_name").send_keys("Selenium A/B Testing Tool")
        driver.find_element_by_id("external_tool_consumer_key").send_keys("test")
        driver.find_element_by_id("external_tool_shared_secret").send_keys("secret")
        Select(driver.find_element_by_id("external_tool_config_type")).select_by_value("by_url")
        driver.find_element_by_id("external_tool_config_url").send_keys(tool_config_url)
        driver.find_element_by_xpath("(//button[@type='button'])[14]").click()

        # Go to the A/B Testing Tool
        time.sleep(5)

        driver.get(self.base_url)
        driver.find_element_by_link_text("A/B Testing Tool").click()

        driver.switch_to_frame("tool_content")    
              
        time.sleep(5)

        # oAuth, if needed
        if self.is_element_present(By.NAME,"commit"):
            # Cancel (deny permission)
            driver.find_element_by_link_text("Cancel").click()
            # Grant permission
            driver.get(self.base_url)
            time.sleep(5)
            driver.find_element_by_link_text("A/B Testing Tool").click()
            driver.switch_to_frame("tool_content") 
            time.sleep(5)   
            driver.find_element_by_name("commit").click()
            time.sleep(5)

        # logout of PIN
        driver.get("http://login.icommons.harvard.edu/pinproxy/logout")
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        # only assertEqual if running locally
        #self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()