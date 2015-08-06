import unittest

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException
from selenium_tests.ab_tool.ab_base_test_case import ABBaseTestCase
from selenium_tests.ab_tool.page_objects.ab_mainpage import MainPage, Locator1
from selenium_tests.ab_tool.page_objects.ab_add_experiment_page import AddExperimentPage, Locator2

# These are simple tests to validate tool loaded, and an experiment can be added and deleted

class test_ab_tool(ABBaseTestCase):

    def test_is_loaded (self):
        """Check that page is loaded by checking against site title of "A/B Testing Dashboard"""
        driver = self.driver
        page = MainPage(driver) #instantiate
        element = page.get_title()
        abtext = "A/B Testing Dashboard"
        print "Verifying page title..."
        self.assertEqual(element.text, abtext, "Error: Wrong page. Expected page title is '{}' but"
                                               " page title is returning '{}'".format(abtext, element.text))


    def test_create_new_experiment(self):
        """This test fills out form to create experiment. Asserts that new experiment is created."""
        #This instantiate the Main Page object and clicks on new experiment button.
        driver = self.driver
        create_experiment = MainPage(driver) #instantiate
        create_experiment.click_to_create_experiment()
        print "Adding an experiment..."
        fill_form = AddExperimentPage(driver)
        fill_form.set_experiment_name("MyExperiment")
        fill_form.add_tracks("My New Track 101")
        fill_form.add_notes("My notes")
        fill_form.is_uniform_random_checked()
        fill_form.submit_experiment()
        try:
            WebDriverWait(driver, 10).until(lambda s: s.find_element(*Locator1._delete_button).is_displayed())
        except TimeoutException:
            return False
        self.assertTrue(driver.find_element(*Locator1._delete_button).is_displayed())

        
    def test_delete_experiment(self):
        """This deletes the experiment, as part of testing delete functionality and test cleanup"""
        driver = self.driver
        delete_experiment = MainPage(driver) #instantiate
        delete_experiment.click_to_begin_delete()
        print "Deleting an experiment..."
        self.assertTrue(delete_experiment.verify_experiment_is_deleted(),
            "Error: Experiment has not been deleted")


if __name__ == "__main__":
    unittest.main()

