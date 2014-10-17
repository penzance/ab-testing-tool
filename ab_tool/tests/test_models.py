from ab_tool.tests.common import SessionTestCase, TEST_COURSE_ID
from ab_tool.models import Track, InterventionPointUrl


class TestModels(SessionTestCase):
    def test_is_missing_urls_true(self):
        """ Tests that is_missing_urls returns false when a url is missing """
        intervention_point = self.create_test_intervention_point()
        track1 = self.create_test_track(name="track1")
        self.create_test_track(name="track2")
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track1, url="example.com")
        self.assertTrue(intervention_point.is_missing_urls())
    
    def test_is_missing_urls_true_no_url(self):
        """ Tests that is_missing_urls returns true when not all urls have urls """
        intervention_point = self.create_test_intervention_point()
        track1 = self.create_test_track()
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track1)
        self.assertTrue(intervention_point.is_missing_urls())
    
    def test_is_missing_urls_true_blank_url(self):
        """ Tests that is_missing_urls returns true when not all urls are filled in """
        intervention_point = self.create_test_intervention_point()
        track1 = self.create_test_track()
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track1, url="")
        self.assertTrue(intervention_point.is_missing_urls())
    
    def test_is_missing_urls_false(self):
        """ Tests that is_missing_urls returns false when all urls are filled """
        intervention_point = self.create_test_intervention_point()
        track1 = self.create_test_track(name="track1")
        track2 = self.create_test_track(name="track2")
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track1, url="http://example.com")
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track2, url="http://example.com")
        self.assertFalse(intervention_point.is_missing_urls())
