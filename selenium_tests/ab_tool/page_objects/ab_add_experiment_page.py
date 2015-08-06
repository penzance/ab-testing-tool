from selenium.webdriver.common.by import By
from selenium_tests.ab_tool.page_objects.ab_base import ABBasePage

# This is the page object of the Add Experiment Page

# Locators for the Add_experiment page###
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

# These are actions that can be taken on the page as part of adding a track

    def set_experiment_name (self, my_experiment_name):
        """Fill in the Experiment Name field when creating a new experiment"""
        name = self.find_element(*Locator2._experimentname)
        name.clear()
        name.send_keys(my_experiment_name)


    def add_tracks (self, newTrackName):
        """Adding a track name when creating a new experiment"""
        new_track_name = self.find_element(*Locator2._new_track_name)
        new_track_name.clear()
        new_track_name.send_keys(newTrackName) 
        self.find_element(*Locator2._add_tracks).click()

    def add_notes (self, notes):
        """Adding notes in the Notes field when creating a new experiment"""
        addnotes = self.find_element(*Locator2._notes_field)
        addnotes.clear()
        addnotes.send_keys(notes)

    def is_uniform_random_checked(self):
        """Validates that uniform random checkbox is checked when creating a new experiment"""
        self.find_element(*Locator2._uniform_checkbox).is_selected()

    def submit_experiment (self):
        """Submit to create a new experiment, and confirm create in the modal popup window"""
        self.find_element(*Locator2._submit_button).click()
        self.find_element(*Locator2._confirm_create).click()


