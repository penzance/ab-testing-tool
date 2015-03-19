# Visit the A/B Testing Tool in a course as a student and assert that the student can visit the intervention point

# Assumes that:
    # STUDENT is a student in this course
    # a page in the course named "Assert" is published
    # the URL for this page is the intervention point URL for all tracks in an experiment
    # the experiment has been started
    # this intervention point has been installed in a module
    # this module is published
    # the module item for this intervention point is published

import pdb
import unittest
import time
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
    NoAlertPresentException)
from settings import (USERNAME, STUDENT, PASSWORD, CANVAS_ENVIRONMENT, CANVAS_BASE_URL,
    TIMESTAMP)

# to run on Jenkins
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

PIN_LOGIN_URL = "https://www.pin1.harvard.edu/cas/login?service=https%3A%2F%2F" + CANVAS_ENVIRONMENT + "%2Flogin%2Fcas"


class add_experiment(unittest.TestCase):
    # setUp to run locally
    """
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = CANVAS_BASE_URL
        self.verificationErrors = []
        self.accept_next_alert = True
    """

    # setUp to run on Jenkins
    def setUp(self):
        self.driver = webdriver.Remote(
           command_executor='http://127.0.0.1:5555/wd/hub',
           desired_capabilities=DesiredCapabilities.FIREFOX)
        self.driver.implicitly_wait(10)
        self.base_url = CANVAS_BASE_URL

    def test_course_login(self):
        driver = self.driver
            
        # log in to PIN
        driver.get(PIN_LOGIN_URL)

        #pdb.set_trace()
        time.sleep(10)

        # select the XID authentication type
        driver.find_element_by_id("compositeAuthenticationSourceType4").click()

        # log in as a student
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys(STUDENT)
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(PASSWORD)
        driver.find_element_by_name("_eventId_submit").click()

        # go to the intervention point in the Selenium test course
        driver.get(CANVAS_BASE_URL + "modules/items/126")

        #pdb.set_trace()
        time.sleep(20)

        # assert that the title of the page in the intervention point is Assert
        current_name = driver.find_element_by_tag_name("h1").text
        title_name = "Assert"
        self.assertEqual(title_name, current_name)
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException: return False
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
        # only assertEqual when running locally
        #self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
