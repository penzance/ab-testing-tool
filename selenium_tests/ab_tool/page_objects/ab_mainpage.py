from selenium.webdriver.common.by import By
from selenium_tests.ab_tool.page_objects.ab_base import ABBasePage
from selenium.common.exceptions import NoSuchElementException

# This is the page object for the Main landing page of AB Tool.

# These are page-specific locators.
class Locator1(object):
    _new_experiment = (By.LINK_TEXT, "New Experiment")
    _h1_selector = (By.CSS_SELECTOR, "h1")
    _name_loc = (By.CSS_SELECTOR, "h3.panel-title.panel-title-experiment")
    _delete_button = (By.CSS_SELECTOR, "[data-selenium-experiment-name='delete_MyExperiment']")
    _delete_confirm = (By.CSS_SELECTOR, "[data-selenium-experiment-name='confirm_delete_MyExperiment']")


class MainPage(ABBasePage):

    def get_title(self):
        """This gets the title of the page you're on to validate the right page loaded"""
        element = self.find_element(*Locator1._h1_selector)
        return element

    def click_to_create_experiment(self):
        """This clicks on the create experiment link on the mainpage"""
        create_experiment = self.find_element(*Locator1._new_experiment)
        create_experiment.click()


    def click_to_begin_delete(self):
        """This clicks on the delete_experiment button on the main page"""
        delete_button = self.find_element(*Locator1._delete_button)
        delete_button.click()
        delete_confirm = self.find_element(*Locator1._delete_confirm)
        delete_confirm.click()


    def verify_experiment_is_deleted(self):
        try:
            self.find_element(*Locator1._delete_button).is_displayed()
        except NoSuchElementException:
            return True
        # If element is found, return False since element is not expected to be present after delete.
        return False



