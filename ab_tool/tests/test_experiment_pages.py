from ab_tool.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_TRACK_ID, NONEXISTENT_EXPERIMENT_ID)
from django.core.urlresolvers import reverse
from ab_tool.models import (Experiment, InterventionPointUrl)
from ab_tool.exceptions import (EXPERIMENT_TRACKS_ALREADY_FINALIZED,
    NO_TRACKS_FOR_EXPERIMENT, UNAUTHORIZED_ACCESS)
import json

class TestExperimentPages(SessionTestCase):
    """ Tests related to Experiment and Experiment pages and methods """
    
    def test_create_experiment_view(self):
        """ Tests editExperiment template renders for url 'create_experiment' """
        response = self.client.get(reverse("ab_testing_tool_create_experiment"))
        self.assertOkay(response)
        self.assertTemplateUsed(response, "ab_tool/editExperiment.html")
    
    def test_create_experiment_view_unauthorized(self):
        """ Tests editExperiment template does not render for url 'create_experiment'
            when unauthorized """
        self.set_roles([])
        response = self.client.get(reverse("ab_testing_tool_create_experiment"), follow=True)
        self.assertTemplateNotUsed(response, "ab_tool/create_experiment.html")
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_edit_experiment_view(self):
        """ Tests editExperiment template renders when authenticated """
        experiment = self.create_test_experiment()
        response = self.client.get(reverse("ab_testing_tool_edit_experiment", args=(experiment.id,)))
        self.assertTemplateUsed(response, "ab_tool/editExperiment.html")
    
    def test_edit_experiment_view_started_experiment(self):
        """ Tests editExperiment template renders when experiment has started """
        experiment = self.create_test_experiment()
        experiment.tracks_finalized = True
        experiment.save()
        response = self.client.get(reverse("ab_testing_tool_edit_experiment", args=(experiment.id,)))
        self.assertTemplateUsed(response, "ab_tool/editExperiment.html")
    
    def test_edit_experiment_view_with_tracks_weights(self):
        """ Tests editExperiment template renders properly with track weights """
        experiment = self.create_test_experiment()
        experiment.assignment_method = Experiment.WEIGHTED_PROBABILITY_RANDOM
        track1 = self.create_test_track(name="track1", experiment=experiment)
        track2 = self.create_test_track(name="track2", experiment=experiment)
        self.create_test_track_weight(experiment=experiment, track=track1)
        self.create_test_track_weight(experiment=experiment, track=track2)
        response = self.client.get(reverse("ab_testing_tool_edit_experiment", args=(experiment.id,)))
        self.assertTemplateUsed(response, "ab_tool/editExperiment.html")
    
    def test_edit_experiment_view_unauthorized(self):
        """ Tests editExperiment template doesn't render when unauthorized """
        self.set_roles([])
        experiment = self.create_test_experiment(course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("ab_testing_tool_edit_experiment", args=(experiment.id,)),
                                   follow=True)
        self.assertTemplateNotUsed(response, "ab_tool/editExperiment.html")
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_edit_experiment_view_nonexistent(self):
        """Tests edit_experiment when experiment does not exist"""
        e_id = NONEXISTENT_EXPERIMENT_ID
        response = self.client.get(reverse("ab_testing_tool_edit_experiment", args=(e_id,)))
        self.assertTemplateNotUsed(response, "ab_tool/editExperiment.html")
        self.assertEquals(response.status_code, 404)
    
    def test_edit_experiment_view_wrong_course(self):
        """ Tests edit_experiment when attempting to access a experiment from a different course """
        experiment = self.create_test_experiment(course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("ab_testing_tool_edit_experiment", args=(experiment.id,)))
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_submit_create_experiment(self):
        """ Tests that create_experiment creates a Experiment object verified by
            DB count when uniformRandom is true"""
        Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        num_experiments = Experiment.objects.count()
        experiment = {
                "name": "experiment", "notes": "hi", "uniformRandom": True,
                "tracks": [{"id": None, "weighting": None, "name": "A"}]
        }
        response = self.client.post(
            reverse("ab_testing_tool_submit_create_experiment"), follow=True,
            content_type="application/json", data=json.dumps(experiment)
        )
        self.assertEquals(num_experiments + 1, Experiment.objects.count(), response)
    
    def test_submit_create_experiment_with_weights_as_assignment_method(self):
        """ Tests that create_experiment creates a Experiment object verified by
            DB count when uniformRandom is false and the tracks have weightings """
        Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        num_experiments = Experiment.objects.count()
        experiment = {
                "name": "experiment", "notes": "hi", "uniformRandom": False,
                "tracks": [{"id": None, "weighting": 100, "name": "A"}]
        }
        response = self.client.post(
            reverse("ab_testing_tool_submit_create_experiment"), follow=True,
            content_type="application/json", data=json.dumps(experiment)
        )
        self.assertEquals(num_experiments + 1, Experiment.objects.count(), response)
    
    def test_submit_create_experiment_unauthorized(self):
        """Tests that create_experiment creates a Experiment object verified by DB count"""
        self.set_roles([])
        Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        num_experiments = Experiment.objects.count()
        experiment = {"name": "experiment", "notes": "hi"}
        response = self.client.post(
            reverse("ab_testing_tool_submit_create_experiment"), follow=True,
            content_type="application/json", data=json.dumps(experiment)
        )
        self.assertEquals(num_experiments, Experiment.objects.count())
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_submit_edit_experiment(self):
        """ Tests that submit_edit_experiment does not change DB count but does change Experiment
            attribute"""
        experiment = self.create_test_experiment(name="old_name")
        experiment_id = experiment.id
        num_experiments = Experiment.objects.count()
        experiment = {
                "name": "new_name", "notes": "hi", "uniformRandom": True,
                "tracks": [{"id": None, "weighting": None, "name": "A"}]
        }
        response = self.client.post(
            reverse("ab_testing_tool_submit_edit_experiment", args=(experiment_id,)),
            follow=True, content_type="application/json", data=json.dumps(experiment)
        )
        self.assertOkay(response)
        self.assertEquals(num_experiments, Experiment.objects.count())
        experiment = Experiment.objects.get(id=experiment_id)
        self.assertEquals(experiment.name, "new_name")
    
    def test_submit_edit_experiment_changes_assignment_method_to_weighted(self):
        """ Tests that submit_edit_experiment changes an Experiment's assignment
            method from uniform (default) to weighted"""
        experiment = self.create_test_experiment(name="old_name")
        experiment_id = experiment.id
        num_experiments = Experiment.objects.count()
        no_track_weights = experiment.track_probabilites.count()
        experiment = {
                "name": "new_name", "notes": "hi", "uniformRandom": False,
                "tracks": [{"id": None, "weighting": 20, "name": "A"},
                           {"id": None, "weighting": 80, "name": "B"}]
        }
        response = self.client.post(
            reverse("ab_testing_tool_submit_edit_experiment", args=(experiment_id,)),
            follow=True, content_type="application/json", data=json.dumps(experiment)
        )
        self.assertOkay(response)
        self.assertEquals(num_experiments, Experiment.objects.count())
        experiment = Experiment.objects.get(id=experiment_id)
        self.assertEquals(experiment.assignment_method, Experiment.WEIGHTED_PROBABILITY_RANDOM)
        self.assertEquals(experiment.track_probabilites.count(), no_track_weights + 2)
    
    def test_submit_edit_experiment_changes_assignment_method_to_uniform(self):
        """ Tests that submit_edit_experiment changes an Experiment's assignment
            method from weighted uniform """
        experiment = self.create_test_experiment(
                name="old_name", assignment_method=Experiment.WEIGHTED_PROBABILITY_RANDOM)
        experiment_id = experiment.id
        num_experiments = Experiment.objects.count()
        no_tracks = experiment.tracks.count()
        experiment = {
                "name": "new_name", "notes": "hi", "uniformRandom": True,
                "tracks": [{"id": None, "weighting": None, "name": "A"},
                           {"id": None, "weighting": None, "name": "B"},
                           {"id": None, "weighting": None, "name": "C"}]
        }
        response = self.client.post(
            reverse("ab_testing_tool_submit_edit_experiment", args=(experiment_id,)),
            follow=True, content_type="application/json", data=json.dumps(experiment)
        )
        self.assertOkay(response)
        self.assertEquals(num_experiments, Experiment.objects.count())
        experiment = Experiment.objects.get(id=experiment_id)
        self.assertEquals(experiment.assignment_method, Experiment.UNIFORM_RANDOM)
        self.assertEquals(experiment.tracks.count(), no_tracks + 3)
    
    def test_submit_edit_experiment_unauthorized(self):
        """ Tests submit_edit_experiment when unauthorized"""
        self.set_roles([])
        experiment = self.create_test_experiment(name="old_name")
        experiment_id = experiment.id
        experiment = {"name": "new_name", "notes": ""}
        response = self.client.post(
            reverse("ab_testing_tool_submit_edit_experiment", args=(experiment_id,)),
            content_type="application/json", data=json.dumps(experiment), follow=True
        )
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_submit_edit_experiment_nonexistent(self):
        """ Tests that submit_edit_experiment method raises error for non-existent Experiment """
        experiment_id = NONEXISTENT_EXPERIMENT_ID
        experiment = {"name": "new_name", "notes": ""}
        response = self.client.post(
            reverse("ab_testing_tool_submit_edit_experiment", args=(experiment_id,)),
            content_type="application/json", data=json.dumps(experiment)
        )
        self.assertEquals(response.status_code, 404)
    
    def test_submit_edit_experiment_wrong_course(self):
        """ Tests that submit_edit_experiment method raises error for existent Experiment but
            for wrong course"""
        experiment = self.create_test_experiment(name="old_name",
                                       course_id=TEST_OTHER_COURSE_ID)
        data = {"name": "new_name", "notes": ""}
        response = self.client.post(
            reverse("ab_testing_tool_submit_edit_experiment", args=(experiment.id,)),
            content_type="application/json", data=json.dumps(data)
        )
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_submit_edit_started_experiment_changes_name_and_notes(self):
        """ Tests that submit_edit_experiment changes an Experiment's 
            name and notes even if the experiment has already been started """
        experiment = self.create_test_experiment(name="old_name", notes="old_notes",
                                                 tracks_finalized=True)
        experiment_id = experiment.id
        num_experiments = Experiment.objects.count()
        experiment = {
                "name": "new_name", "notes": "new_notes", "tracks": [],
        }
        response = self.client.post(
            reverse("ab_testing_tool_submit_edit_experiment", args=(experiment_id,)),
            follow=True, content_type="application/json", data=json.dumps(experiment)
        )
        self.assertOkay(response)
        self.assertEquals(num_experiments, Experiment.objects.count())
        experiment = Experiment.objects.get(id=experiment_id)
        self.assertEquals(experiment.name, "new_name")
        self.assertEquals(experiment.notes, "new_notes")
    
    def test_submit_edit_started_experiment_does_not_change_tracks(self):
        """ Tests that submit_edit_experiment doesn't change tracks for
            an experiment that has already been started """
        experiment = self.create_test_experiment(name="old_name", tracks_finalized=True,
                assignment_method=Experiment.WEIGHTED_PROBABILITY_RANDOM)
        experiment_id = experiment.id
        num_experiments = Experiment.objects.count()
        no_tracks = experiment.tracks.count()
        experiment = {
                "name": "new_name", "notes": "hi", "uniformRandom": True,
                "tracks": [{"id": None, "weighting": None, "name": "A"},
                           {"id": None, "weighting": None, "name": "B"},
                           {"id": None, "weighting": None, "name": "C"}]
        }
        response = self.client.post(
            reverse("ab_testing_tool_submit_edit_experiment", args=(experiment_id,)),
            follow=True, content_type="application/json", data=json.dumps(experiment)
        )
        self.assertOkay(response)
        self.assertEquals(num_experiments, Experiment.objects.count())
        experiment = Experiment.objects.get(id=experiment_id)
        self.assertEquals(experiment.assignment_method, Experiment.WEIGHTED_PROBABILITY_RANDOM)
        self.assertEquals(experiment.tracks.count(), no_tracks)
    
    def test_delete_experiment(self):
        """ Tests that delete_experiment method properly deletes a experiment when authorized"""
        first_num_experiments = Experiment.objects.count()
        experiment = self.create_test_experiment()
        self.assertEqual(first_num_experiments + 1, Experiment.objects.count())
        response = self.client.get(reverse("ab_testing_tool_delete_experiment", args=(experiment.id,)),
                                   follow=True)
        second_num_experiments = Experiment.objects.count()
        self.assertOkay(response)
        self.assertEqual(first_num_experiments, second_num_experiments)
    
    def test_delete_experiment_already_finalized(self):
        """ Tests that delete experiment doesn't work when experiments are finalized """
        experiment = self.create_test_experiment()
        experiment.update(tracks_finalized=True)
        first_num_experiments = Experiment.objects.count()
        response = self.client.get(reverse("ab_testing_tool_delete_experiment", args=(experiment.id,)),
                                   follow=True)
        second_num_experiments = Experiment.objects.count()
        self.assertError(response, EXPERIMENT_TRACKS_ALREADY_FINALIZED)
        self.assertEqual(first_num_experiments, second_num_experiments)
    
    def test_delete_experiment_unauthorized(self):
        """ Tests that delete_experiment method raises error when unauthorized """
        self.set_roles([])
        experiment = self.create_test_experiment()
        first_num_experiments = Experiment.objects.count()
        response = self.client.get(reverse("ab_testing_tool_delete_experiment", args=(experiment.id,)),
                                   follow=True)
        second_num_experiments = Experiment.objects.count()
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
        self.assertEqual(first_num_experiments, second_num_experiments)
    
    def test_delete_experiment_nonexistent(self):
        """ Tests that delete_experiment method raises error for non-existent Experiment """
        self.create_test_experiment()
        t_id = NONEXISTENT_TRACK_ID
        first_num_experiments = Experiment.objects.count()
        response = self.client.get(reverse("ab_testing_tool_delete_experiment", args=(t_id,)), follow=True)
        second_num_experiments = Experiment.objects.count()
        self.assertEqual(first_num_experiments, second_num_experiments)
        self.assertEquals(response.status_code, 404)
    
    def test_delete_experiment_wrong_course(self):
        """ Tests that delete_experiment method raises error for existent Experiment but for
            wrong course """
        experiment = self.create_test_experiment(course_id=TEST_OTHER_COURSE_ID)
        first_num_experiments = Experiment.objects.count()
        response = self.client.get(reverse("ab_testing_tool_delete_experiment", args=(experiment.id,)),
                                   follow=True)
        second_num_experiments = Experiment.objects.count()
        self.assertEqual(first_num_experiments, second_num_experiments)
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_delete_experiment_deletes_intervention_point_urls(self):
        """ Tests that intervention_point_urls of a experiment are deleted when the experiment is """
        experiment = self.create_test_experiment()
        track1 = self.create_test_track(name="track1", experiment=experiment)
        track2 = self.create_test_track(name="track2", experiment=experiment)
        intervention_point = self.create_test_intervention_point()
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track1, url="example.com")
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track2, url="example.com")
        first_num_intervention_point_urls = InterventionPointUrl.objects.count()
        response = self.client.get(reverse("ab_testing_tool_delete_experiment", args=(experiment.id,)),
                                   follow=True)
        second_num_intervention_point_urls = InterventionPointUrl.objects.count()
        self.assertOkay(response)
        self.assertEqual(first_num_intervention_point_urls - 2, second_num_intervention_point_urls)
    
    def test_finalize_tracks(self):
        """ Tests that the finalize tracks page sets the appropriate course """
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertFalse(experiment.tracks_finalized)
        self.create_test_track()
        response = self.client.get(reverse("ab_testing_tool_finalize_tracks", args=(experiment.id,)),
                                   follow=True)
        self.assertOkay(response)
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertTrue(experiment.tracks_finalized)
    
    def test_finalize_tracks_missing_urls(self):
        """ Tests that finalize fails if there are missing urls """
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertFalse(experiment.tracks_finalized)
        track1 = self.create_test_track(name="track1", experiment=experiment)
        self.create_test_track(name="track2", experiment=experiment)
        intervention_point = self.create_test_intervention_point()
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track1, url="example.com")
        self.client.get(reverse("ab_testing_tool_finalize_tracks", args=(experiment.id,)),
                        follow=True)
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertFalse(experiment.tracks_finalized)
    
    def test_finalize_tracks_no_tracks(self):
        """ Tests that finalize fails if there are no tracks for an experiment """
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        response = self.client.get(reverse("ab_testing_tool_finalize_tracks", args=(experiment.id,)),
                                   follow=True)
        self.assertError(response, NO_TRACKS_FOR_EXPERIMENT)
    
    def test_finalize_tracks_missing_track_weights(self):
        """ Tests that finalize fails if there are no track weights for an weighted
            probability experiment """
        experiment = self.create_test_experiment(assignment_method=Experiment.WEIGHTED_PROBABILITY_RANDOM)
        self.create_test_track(name="track1", experiment=experiment)
        self.client.get(reverse("ab_testing_tool_finalize_tracks", args=(experiment.id,)),
                                   follow=True)
        self.assertFalse(experiment.tracks_finalized)
