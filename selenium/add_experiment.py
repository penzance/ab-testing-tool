# Add experiment to the A/B Testing Tool in a course

import pdb
import unittest
import time
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
    NoAlertPresentException)
from settings import (USERNAME, PASSWORD, CANVAS_ENVIRONMENT, CANVAS_BASE_URL,
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

        # log in
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys(USERNAME)
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(PASSWORD)
        driver.find_element_by_name("_eventId_submit").click()

        # go to the Selenium test course
        driver.get(self.base_url)

        #pdb.set_trace()

        # Go to the A/B Testing Tool and add an uniform experiment to have 2 tracks
        driver.find_element_by_link_text("A/B Testing Tool").click()
        driver.switch_to_frame("tool_content")
        driver.find_element_by_link_text("New Experiment").click()
        driver.find_element_by_name("experimentName").send_keys("%s Test Add Uniform Experiment" %TIMESTAMP)
        if not driver.find_element_by_name("uniformRandom").is_selected():
            driver.find_element_by_name("uniformRandom").click()
        driver.find_element_by_name("experimentNotes").send_keys("Selenium test for add_experiment. Select Uniform Random with 2 tracks.")
        driver.find_element_by_id("create-confirm").click()
        driver.find_element_by_id("createNow").click()

        driver.switch_to_frame("tool_content")
        current_name = driver.find_element_by_tag_name("h1").text
        title_name = "A/B Testing Tool"
        self.assertEqual(title_name, current_name)
        # Add an intervention point with no URLs
        # need to be able to find element by link_text to work
        #driver.find_element_by_id("add_intervention_point_button").click()
        #driver.find_element_by_name("name").clear()
        #driver.find_element_by_name("name").send_keys("%s Selenium Add Intervention Point" %TIMESTAMP)
        #driver.find_element_by_link_text("Create").click()

        # Log out of PIN
        driver.get("http://login.icommons.harvard.edu/pinproxy/logout")
    
    
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
