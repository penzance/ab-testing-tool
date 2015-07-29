from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
import unittest, time, re
from selenium_tests.ab_tool.ab_base_test_case import ABBaseTestCase
from selenium_tests.ab_tool.page_objects.ab_mainpage import MainPage, Locator1
from selenium_tests.ab_tool.page_objects.ab_add_experiment_page import AddExperimentPage, Locator2

# These are simple tests to validate that the tool has loaded,
# as well as validate that an experiment can be added and deleted"""

class test_ab_tool(ABBaseTestCase):

    def test_is_loaded (self):
        """Check that page is loaded by checking against site title of "A/B Testing Dashboard"""
        driver = self.driver
        page = MainPage(driver) #instantiate
        element = page.get_title()
        abtext = "A/B Testing Dashboard"
        print element.text
        print "Working on verifying that the right page loaded..."
        driver.save_screenshot('page_after_login.png')
        self.assertEqual(element.text, abtext, element.text)


    def test_create_new_experiment(self):
        """This test fills out form to create experiment. Asserts that new experiment is created."""
        #This instantiate the Main Page object and clicks on the new experiment button.
        driver = self.driver
        create_experiment = MainPage(driver) #instantiate
        create_experiment.click_to_create_experiment()
        fill_form = AddExperimentPage(driver)
        fill_form.create_name(driver,"MyExperiment")
        fill_form.add_tracks(driver,"My New Track 101")
        fill_form.add_notes(driver,"My notes")
        fill_form.submit_experiment(driver)
        fill_form.is_checked(driver)
        try:
            WebDriverWait(driver, 10).until(lambda s: s.find_element(*Locator2._experimentname).is_displayed())
        except TimeoutException:
            return False
        self.assertTrue(self, driver.find_element_by_css_selector("[data-selenium-experiment-name='delete_MyExperiment']"))


        
    def test_delete_experiment(self):
        """This deletes the experiment, as part of testing delete functionality and test cleanup"""
        driver = self.driver
        delete_experiment = MainPage(driver) #instantiate
        print "Deleting experiment..."
        delete_experiment.delete_experiment()
        delete_experiment.delete_confirm()
        driver.save_screenshot('delete_experiment.png')


if __name__ == "__main__":
    unittest.main()

