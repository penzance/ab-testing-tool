from ab_tool.tests.common import SessionTestCase, TEST_COURSE_ID
from ab_tool.models import (Track, InterventionPointUrl, Experiment,
    TrackProbabilityWeight, InterventionPoint)
import json
from django.db import IntegrityError
from mock import patch
from ab_tool.exceptions import DATABASE_ERROR


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
    
    def test_experiment_new_track(self):
        """ Tests that the new_track method of an experiment creates a new track """
        experiment = self.create_test_experiment()
        num_tracks = experiment.tracks.count()
        track = experiment.new_track("new_track")
        self.assertEqual(track.name, "new_track")
        self.assertEqual(num_tracks + 1, experiment.tracks.count())
    
    def test_experiment_to_json(self):
        """ Tests that the json returned by experiment's to_json method
            contains expeced properties """
        experiment = self.create_test_experiment(
                name="test_experiment", assignment_method=Experiment.UNIFORM_RANDOM)
        self.create_test_track(name="track1", experiment=experiment)
        self.create_test_track(name="track2", experiment=experiment)
        experiment_dict = json.loads(experiment.to_json())
        self.assertEqual(experiment_dict["name"], "test_experiment")
        self.assertEqual(len(experiment_dict["tracks"]), 2)
        self.assertEqual(experiment_dict["uniformRandom"], True)
    
    def test_track_get_weighting(self):
        """ Tests that get_weighting returns the weighting of the track """
        track = self.create_test_track()
        self.create_test_track_weight(weighting=42, track=track)
        self.assertEqual(track.get_weighting(), 42)
    
    def test_track_get_weighting_none(self):
        """ Tests that get_weighting returns None if the track has no weighting """
        track = self.create_test_track()
        self.assertEqual(track.get_weighting(), None)
    
    def test_track_set_weighting(self):
        """ Tests that set_weighting sets the weighting for a track """
        track = self.create_test_track()
        track.set_weighting(42)
        self.assertEqual(track.weight.weighting, 42)
        track2 = self.create_test_track(name="track2")
        track2.set_weighting(None)
        self.assertEqual(track2.weight.weighting, 0)
    
    def test_track_set_weighting_existing_weight(self):
        """ Tests that set_weighting overrides existing weight for a track """
        track = self.create_test_track()
        self.create_test_track_weight(weighting=100, track=track)
        self.assertEqual(track.weight.weighting, 100)
        track.set_weighting(42)
        self.assertEqual(track.weight.weighting, 42)
    
    def test_copy_experiment_copies_objects(self):
        """ Tests that copy experiment creates the appropriate numbers of new
            objects """
        experiment = self.create_test_experiment()
        tracks = [self.create_test_track(experiment=experiment, name=str(i))
                  for i in range(4)]
        intervention_points = [
                self.create_test_intervention_point(name=str(i), experiment=experiment)
                for i in range(2)
        ]
        for track in tracks:
            track.set_weighting(25)
            for intervention_point in intervention_points:
                InterventionPointUrl.objects.create(
                        intervention_point=intervention_point, track=track,
                        url="http://example.com"
                )
        num_experiments = Experiment.objects.count()
        num_tracks = Track.objects.count()
        num_track_weights = TrackProbabilityWeight.objects.count()
        num_ips = InterventionPoint.objects.count()
        num_ip_urls = InterventionPointUrl.objects.count()
        experiment.copy("new_name")
        self.assertEqual(Experiment.objects.count(), num_experiments + 1)
        self.assertEqual(Track.objects.count(), num_tracks + 4)
        self.assertEqual(TrackProbabilityWeight.objects.count(), num_track_weights + 4)
        self.assertEqual(InterventionPoint.objects.count(), num_ips + 2)
        self.assertEqual(InterventionPointUrl.objects.count(), num_ip_urls + 8)
    
    @patch("django.db.models.Model.save", side_effect=IntegrityError("error"))
    def test_object_update_raises_integrity_error(self, _mock1):
        """ Tests that database error is raised. The patch creates a fake database conflict """
        self.assertRaisesSpecific(DATABASE_ERROR("error"), self.create_test_track)
        self.assertRaisesSpecific(DATABASE_ERROR("error"), self.create_test_track_weight)
        self.assertRaisesSpecific(DATABASE_ERROR("error"), self.create_test_experiment)
    
    @patch("django.db.models.Model.save", return_value=None)
    def test_object_save_doesnt_raise_error(self, _mock1):
        """ Tests no database error is raised """
        self.create_test_experiment()
        self.assertEquals(_mock1.call_count, 1)
