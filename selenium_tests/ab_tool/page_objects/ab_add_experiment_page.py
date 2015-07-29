"""This is the page object of the Add Experiment Page"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_tests.ab_tool.page_objects.ab_base import ABBasePage
from selenium.common.exceptions import NoSuchElementException


### Locators for the Add_experiment page###
class Locator2(object):
    _experimentname = (By.ID, "experimentName") 
    _notes_field = (By.ID, "experimentNotes")
    _new_track_name = (By.ID,"newTrackName")
    _add_tracks = (By.ID, "addTrack") 
    _submit_button = (By.ID, "create-confirm")
    _confirm_create = (By.ID, "createNow")
    _uniform_checkbox = (By.ID, "uniformRandom")
    _trash_icon = (By.CSS_SELECTOR, "i.fa.fa-trash")

class AddExperimentPage(ABBasePage):
    def __init__(self, driver):
        super(AddExperimentPage, self).__init__(driver)  
    

#These are actions that can be taken on the page as part of adding a track

    def create_name (self,driver,my_experiment_name):
        """Fill in the Experiment Name field when creating a new experiment"""
        name = driver.find_element(*Locator2._experimentname)
        name.clear()
        name.send_keys(my_experiment_name)


    def add_tracks (self,driver,newTrackName):
        """Adding a track name when creating a new experiment"""
        new_track_name = driver.find_element(*Locator2._new_track_name)
        new_track_name.send_keys(newTrackName) 
        driver.find_element(*Locator2._add_tracks).click()

    def add_notes (self,driver,notes):
        """Adding notes in the Notes field when creating a new experiment"""
        addnotes = driver.find_element(*Locator2._notes_field)
        addnotes.clear()
        addnotes.send_keys(notes) 

    def submit_experiment (self,driver):
        """Submit to create a new experiment, and confirm create in the modal popup window"""
        submit = driver.find_element(*Locator2._submit_button).click()
        confirm = driver.find_element(*Locator2._confirm_create).click()


    def is_checked(self, driver):
        """Validates that uniform random checkbox is checked when creating a new experiment"""
        try:
            print "Working on adding a new experiment...:  %s" % self._driver.current_url
            checked = driver.find_element(*Locator2._uniform_checkbox).is_selected()
        except NoSuchElementException:

            try:
                self.focus_on_tool_frame()
                checked = driver.find_element(*Locator2._uniform_checkbox).is_selected()
                return checked
            except:
                return False
