from ab_tool.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_TRACK_ID, NONEXISTENT_EXPERIMENT_ID)
from django.core.urlresolvers import reverse
from ab_tool.models import Track, Experiment, InterventionPointUrl
from ab_tool.exceptions import (EXPERIMENT_TRACKS_ALREADY_FINALIZED,
    NO_TRACKS_FOR_EXPERIMENT, UNAUTHORIZED_ACCESS)

class TestExperimentPages(SessionTestCase):
    """ Tests related to Experiment and Experiment pages and methods """
    
    def test_create_experiment_view(self):
        """ Tests edit_experiment template renders for url 'create_experiment' """
        response = self.client.get(reverse("ab:create_experiment"))
        self.assertOkay(response)
        self.assertTemplateUsed(response, "ab_tool/edit_experiment.html")

    def test_create_experiment_view_unauthorized(self):
        """ Tests edit_experiment template does not render for url 'create_experiment'
            when unauthorized """
        self.set_roles([])
        response = self.client.get(reverse("ab:create_experiment"), follow=True)
        self.assertTemplateNotUsed(response, "ab_tool/create_experiment.html")
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")

    def test_edit_experiment_view(self):
        """ Tests edit_experiment template renders when authenticated """
        experiment = self.create_test_experiment()
        response = self.client.get(reverse("ab:edit_experiment", args=(experiment.id,)))
        self.assertTemplateUsed(response, "ab_tool/edit_experiment.html")

    def test_edit_experiment_view_unauthorized(self):
        """ Tests edit_experiment template renders when unauthorized """
        self.set_roles([])
        experiment = self.create_test_experiment(course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("ab:edit_experiment", args=(experiment.id,)),
                                   follow=True)
        self.assertTemplateNotUsed(response, "ab_tool/edit_experiment.html")
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")

    def test_edit_experiment_view_nonexistent(self):
        """Tests edit_experiment when experiment does not exist"""
        e_id = NONEXISTENT_EXPERIMENT_ID
        response = self.client.get(reverse("ab:edit_experiment", args=(e_id,)))
        self.assertTemplateNotUsed(response, "ab_tool/edit_experiment.html")
        self.assertEquals(response.status_code, 404)

    def test_edit_experiment_view_wrong_course(self):
        """ Tests edit_experiment when attempting to access a experiment from a different course """
        experiment = self.create_test_experiment(course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("ab:edit_experiment", args=(experiment.id,)))
        self.assertError(response, UNAUTHORIZED_ACCESS)

    def test_submit_create_experiment(self):
        """Tests that create_experiment creates a Experiment object verified by DB count"""
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        num_experiments = Experiment.objects.count()
        data = {"name": "experiment", "notes": "hi", "assignment_method": 1, "uniform_tracks": 2 }
        response = self.client.post(reverse("ab:submit_create_experiment"),
                                    data, follow=True)
        self.assertEquals(num_experiments + 1, Experiment.objects.count(), response)

    def test_submit_create_experiment_with_weights_as_assignment_method(self):
        """Tests that create_experiment creates a Experiment object verified by DB count"""
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        num_experiments = Experiment.objects.count()
        data = {"name": "experiment", "notes": "hi", "assignment_method": 2, "track_weights[]": [2,4] }
        response = self.client.post(reverse("ab:submit_create_experiment"),
                                    data, follow=True)
        self.assertEquals(num_experiments + 1, Experiment.objects.count(), response)

    def test_submit_create_experiment_unauthorized(self):
        """Tests that create_experiment creates a Experiment object verified by DB count"""
        self.set_roles([])
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        num_experiments = Experiment.objects.count()
        data = {"name": "experiment", "notes": "hi"}
        response = self.client.post(reverse("ab:submit_create_experiment"),
                                    data, follow=True)
        self.assertEquals(num_experiments, Experiment.objects.count())
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")

    def test_submit_edit_experiment(self):
        """ Tests that submit_edit_experiment does not change DB count but does change Experiment
            attribute"""
        experiment = self.create_test_experiment(name="old_name")
        experiment_id = experiment.id
        num_experiments = Experiment.objects.count()
        data = {"name": "new_name", "notes": "", "assignment_method": 1, "uniform_tracks": 2}
        response = self.client.post(
                reverse("ab:submit_edit_experiment", args=(experiment_id,)), data, follow=True)
        self.assertOkay(response)
        self.assertEquals(num_experiments, Experiment.objects.count())
        experiment = Experiment.objects.get(id=experiment_id)
        self.assertEquals(experiment.name, "new_name")

    def test_submit_edit_experiment_unauthorized(self):
        """ Tests submit_edit_experiment when unauthorized"""
        self.set_roles([])
        experiment = self.create_test_experiment(name="old_name")
        experiment_id = experiment.id
        data = {"name": "new_name", "notes": ""}
        response = self.client.post(
                reverse("ab:submit_edit_experiment", args=(experiment_id,)), data, follow=True)
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")

    def test_submit_edit_experiment_nonexistent(self):
        """ Tests that submit_edit_experiment method raises error for non-existent Experiment """
        experiment_id = NONEXISTENT_EXPERIMENT_ID
        data = {"name": "new_name", "notes": ""}
        response = self.client.post(
                reverse("ab:submit_edit_experiment", args=(experiment_id,)), data, follow=True)
        self.assertEquals(response.status_code, 404)

    def test_submit_edit_experiment_wrong_course(self):
        """ Tests that submit_edit_experiment method raises error for existent Experiment but
            for wrong course"""
        experiment = self.create_test_experiment(name="old_name",
                                       course_id=TEST_OTHER_COURSE_ID)
        data = {"name": "new_name", "notes": ""}
        response = self.client.post(
                reverse("ab:submit_edit_experiment", args=(experiment.id,)), data, follow=True)
        self.assertError(response, UNAUTHORIZED_ACCESS)

    def test_delete_experiment(self):
        """ Tests that delete_experiment method properly deletes a experiment when authorized"""
        first_num_experiments = Experiment.objects.count()
        experiment = self.create_test_experiment()
        self.assertEqual(first_num_experiments + 1, Experiment.objects.count())
        response = self.client.get(reverse("ab:delete_experiment", args=(experiment.id,)),
                                   follow=True)
        second_num_experiments = Experiment.objects.count()
        self.assertOkay(response)
        self.assertEqual(first_num_experiments, second_num_experiments)

    def test_delete_experiment_already_finalized(self):
        """ Tests that delete experiment doesn't work when experiments are finalized """
        experiment = self.create_test_experiment()
        experiment.update(tracks_finalized=True)
        first_num_experiments = Experiment.objects.count()
        response = self.client.get(reverse("ab:delete_experiment", args=(experiment.id,)),
                                   follow=True)
        second_num_experiments = Experiment.objects.count()
        self.assertError(response, EXPERIMENT_TRACKS_ALREADY_FINALIZED)
        self.assertEqual(first_num_experiments, second_num_experiments)

    def test_delete_experiment_unauthorized(self):
        """ Tests that delete_experiment method raises error when unauthorized """
        self.set_roles([])
        experiment = self.create_test_experiment()
        first_num_experiments = Experiment.objects.count()
        response = self.client.get(reverse("ab:delete_experiment", args=(experiment.id,)),
                                   follow=True)
        second_num_experiments = Experiment.objects.count()
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
        self.assertEqual(first_num_experiments, second_num_experiments)

    def test_delete_experiment_nonexistent(self):
        """ Tests that delete_experiment method raises error for non-existent Experiment """
        self.create_test_experiment()
        t_id = NONEXISTENT_TRACK_ID
        first_num_experiments = Experiment.objects.count()
        response = self.client.get(reverse("ab:delete_experiment", args=(t_id,)), follow=True)
        second_num_experiments = Experiment.objects.count()
        self.assertEqual(first_num_experiments, second_num_experiments)
        self.assertEquals(response.status_code, 404)

    def test_delete_experiment_wrong_course(self):
        """ Tests that delete_experiment method raises error for existent Experiment but for
            wrong course """
        experiment = self.create_test_experiment(course_id=TEST_OTHER_COURSE_ID)
        first_num_experiments = Experiment.objects.count()
        response = self.client.get(reverse("ab:delete_experiment", args=(experiment.id,)),
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
        response = self.client.get(reverse("ab:delete_experiment", args=(experiment.id,)),
                                   follow=True)
        second_num_intervention_point_urls = InterventionPointUrl.objects.count()
        self.assertOkay(response)
        self.assertEqual(first_num_intervention_point_urls - 2, second_num_intervention_point_urls)
    
    def test_finalize_tracks(self):
        """ Tests that the finalize tracks page sets the appropriate course """
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertFalse(experiment.tracks_finalized)
        self.create_test_track()
        response = self.client.get(reverse("ab:finalize_tracks", args=(experiment.id,)),
                                   follow=True)
        self.assertOkay(response)
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertTrue(experiment.tracks_finalized)
    
    def test_finalize_tracks_missing_urls(self):
        """ Tests that finalize fails if there are missing urls """
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertFalse(experiment.tracks_finalized)
        track1 = self.create_test_track(name="track1")
        self.create_test_track(name="track2")
        intervention_point = self.create_test_intervention_point()
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track1, url="example.com")
        self.client.get(reverse("ab:finalize_tracks", args=(experiment.id,)),
                        follow=True)
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertFalse(experiment.tracks_finalized)
    
    def test_finalize_tracks_no_experiments(self):
        """ Tests that finalize fails if there are no experiments """
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        response = self.client.get(reverse("ab:finalize_tracks", args=(experiment.id,)),
                                   follow=True)
        self.assertError(response, NO_TRACKS_FOR_EXPERIMENT)
