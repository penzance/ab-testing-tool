from ab_tool.tests.common import SessionTestCase, TEST_COURSE_ID
from ab_tool.models import Track, InterventionPointUrl, Experiment,\
    TrackProbabilityWeight
from ab_tool.exceptions import TRACK_WEIGHTS_ERROR


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
    
    def test_set_number_of_tracks_no_change(self):
        """ Tests that set_number_of_tracks returns without change when int parameter
            passed to it is equal to the current number of tracks for an Experiment
            object """
        experiment = self.create_test_experiment()
        track1 = self.create_test_track(name="track1", experiment=experiment)
        track2 = self.create_test_track(name="track2", experiment=experiment)
        num = experiment.tracks.count()
        experiment.set_number_of_tracks(num)
        self.assertTrue(experiment.tracks.count() == num)
        self.assertTrue(track1 in experiment.tracks.all())
        self.assertTrue(track2 in experiment.tracks.all())

    def test_set_number_of_tracks_adds_tracks(self):
        """ Tests that set_number_of_tracks creates tracks when int parameter
            passed to it is greater to the current number of tracks for an Experiment
            object """
        experiment = self.create_test_experiment()
        track1 = self.create_test_track(name="track1", experiment=experiment)
        track2 = self.create_test_track(name="track2", experiment=experiment)
        num = experiment.tracks.count()
        experiment.set_number_of_tracks(num + 3)
        self.assertTrue(experiment.tracks.count() == (num + 3))
        self.assertTrue(track1 in experiment.tracks.all())
        self.assertTrue(track2 in experiment.tracks.all())
    
    def test_set_number_of_tracks_deletes_tracks(self):
        """ Tests that set_number_of_tracks deletes tracks when int parameter
            passed to it is less to the current number of tracks for an Experiment
            object """
        experiment = self.create_test_experiment()
        track1 = self.create_test_track(name="track1", experiment=experiment)
        track2 = self.create_test_track(name="track2", experiment=experiment)
        num = experiment.tracks.count()
        experiment.set_number_of_tracks(num - 1)
        self.assertTrue(experiment.tracks.count() == (num - 1))
        self.assertTrue(track1 in experiment.tracks.all())
        self.assertTrue(track2 not in experiment.tracks.all())
    
    def test_set_track_weights_raises_error(self):
        experiment = self.create_test_experiment()
        track1 = self.create_test_track(name="track1", experiment=experiment)
        track2 = self.create_test_track(name="track2", experiment=experiment)
        weights_list = [30]
        self.assertRaisesSpecific(TRACK_WEIGHTS_ERROR, experiment.set_track_weights, weights_list)
    
    def test_set_track_weights_updates_weights(self):
        experiment = self.create_test_experiment()
        track1 = self.create_test_track(name="track1", experiment=experiment)
        track2 = self.create_test_track(name="track2", experiment=experiment)
        track1_weight = self.create_test_track_weight(track=track1, experiment=experiment)
        track2_weight = self.create_test_track_weight(track=track2, experiment=experiment)
        weights_list = [30, 70]
        experiment.set_track_weights(weights_list)
        self.assertTrue(experiment.track_probabilites.count() == len(weights_list))
        self.assertTrue(TrackProbabilityWeight.objects.get(pk=track1_weight.id).weighting == weights_list[0])
        self.assertTrue(TrackProbabilityWeight.objects.get(pk=track2_weight.id).weighting == weights_list[1])
    
    def test_set_track_weights_creates_weights(self):
        experiment = self.create_test_experiment()
        track1 = self.create_test_track(name="track1", experiment=experiment)
        track2 = self.create_test_track(name="track2", experiment=experiment)
        weights_list = [30, 70]
        experiment.set_track_weights(weights_list)
        self.assertTrue(experiment.track_probabilites.count() == len(weights_list))
