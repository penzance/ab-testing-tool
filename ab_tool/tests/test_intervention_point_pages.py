from django.core.urlresolvers import reverse
from mock import patch

from ab_tool.constants import STAGE_URL_TAG, DEPLOY_OPTION_TAG
from ab_tool.models import (InterventionPoint, InterventionPointUrl,
    ExperimentStudent, Experiment)
from ab_tool.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_STAGE_ID, APIReturn, LIST_MODULES,
    TEST_STUDENT_ID)
from ab_tool.exceptions import (NO_URL_FOR_TRACK,  UNAUTHORIZED_ACCESS,
    EXPERIMENT_TRACKS_NOT_FINALIZED, NO_TRACKS_FOR_EXPERIMENT,
    DELETING_INSTALLED_STAGE)


class TestInterventionPointPages(SessionTestCase):
    """ Tests related to InterventionPoint related pages and methods """
    def test_deploy_intervention_point_admin(self):
        """ Tests deploy intervention_point for admins redirects to edit intervention_point """
        intervention_point = self.create_test_intervention_point()
        response = self.client.get(reverse("ab_testing_tool_deploy_intervention_point",
                                           args=(intervention_point.id,)))
        self.assertRedirects(response, reverse("ab_testing_tool_modules_page_view_intervention_point",
                                               args=(intervention_point.id,)))
    
    def test_deploy_intervention_point_student_not_finalized(self):
        """ Tests deploy intervention_point for student errors if tracks not finalized
            for the course """
        self.set_roles([])
        intervention_point = self.create_test_intervention_point()
        response = self.client.get(reverse("ab_testing_tool_deploy_intervention_point",
                                           args=(intervention_point.id,)))
        self.assertError(response, EXPERIMENT_TRACKS_NOT_FINALIZED)
    
    def test_deploy_intervention_point_no_tracks_error(self):
        """ Tests deploy intervention_point for student creates errors with no tracks """
        self.set_roles([])
        Experiment.get_placeholder_course_experiment(TEST_COURSE_ID).update(tracks_finalized=True)
        intervention_point = self.create_test_intervention_point()
        response = self.client.get(reverse("ab_testing_tool_deploy_intervention_point",
                                           args=(intervention_point.id,)))
        self.assertError(response, NO_TRACKS_FOR_EXPERIMENT)
    
    def test_deploy_intervention_point_student_created(self):
        """ Tests deploy intervention_point for student creates student object and assigns
            track to that student object """
        self.set_roles([])
        Experiment.get_placeholder_course_experiment(TEST_COURSE_ID).update(tracks_finalized=True)
        intervention_point = self.create_test_intervention_point()
        track = self.create_test_track(name="track1")
        students = ExperimentStudent.objects.filter(course_id=TEST_COURSE_ID,
                                               student_id=TEST_STUDENT_ID)
        self.assertEqual(students.count(), 0)
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track,
                                url="http://www.example.com")
        self.client.get(reverse("ab_testing_tool_deploy_intervention_point", args=(intervention_point.id,)))
        student = ExperimentStudent.objects.get(course_id=TEST_COURSE_ID,
                                            student_id=TEST_STUDENT_ID)
        self.assertEqual(student.track.name, "track1")
    
    def test_deploy_intervention_point_student_redirect(self):
        """ Tests deploy intervention_point for student redirects to the correct url """
        self.set_roles([])
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        experiment.update(tracks_finalized=True)
        intervention_point = self.create_test_intervention_point(name="intervention_point1")
        track = self.create_test_track(name="track1")
        intervention_point2 = self.create_test_intervention_point(name="intervention_point2")
        track2 = self.create_test_track(name="track2")
        ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, experiment=experiment,
                                         student_id=TEST_STUDENT_ID, track=track)
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track,
                                            url="http://www.example.com")
        InterventionPointUrl.objects.create(intervention_point=intervention_point2, track=track2,
                                            url="http://www.incorrect-domain.com")
        response = self.client.get(reverse("ab_testing_tool_deploy_intervention_point",
                                           args=(intervention_point.id,)))
        # Can't use assertRedirects because it is an external domain
        self.assertEqual(response._headers['location'],
                         ("Location", "http://www.example.com"))
        self.assertEqual(response.status_code, 302)
    
    def test_deploy_intervention_point_no_url(self):
        """ Tests deploy intervention_point with existing InterventionPointUrl
            for student with NO_URL_FOR_TRACK error """
        self.set_roles([])
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        experiment.update(tracks_finalized=True)
        intervention_point = self.create_test_intervention_point()
        track = self.create_test_track()
        ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, experiment=experiment,
                                         student_id=TEST_STUDENT_ID, track=track)
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track, url="")
        response = self.client.get(reverse("ab_testing_tool_deploy_intervention_point",
                                           args=(intervention_point.id,)))
        self.assertError(response, NO_URL_FOR_TRACK)
    
    def test_deploy_intervention_point_with_no_interventionpointurl_created(self):
        """ Tests deploy intervention_point with no InterventionPointUrl
            for student with NO_URL_FOR_TRACK error """
        self.set_roles([])
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        experiment.update(tracks_finalized=True)
        intervention_point = self.create_test_intervention_point()
        track = self.create_test_track()
        ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, experiment=experiment,
                                         student_id=TEST_STUDENT_ID, track=track)
        response = self.client.get(reverse("ab_testing_tool_deploy_intervention_point",
                                           args=(intervention_point.id,)))
        self.assertError(response, NO_URL_FOR_TRACK)
    
    def test_deploy_intervention_point_with_url_as_new_tab(self):
        """ Tests deploy intervention_point successfully loads url as new tab"""
        self.set_roles([])
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        experiment.update(tracks_finalized=True)
        intervention_point = self.create_test_intervention_point()
        track = self.create_test_track()
        ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, experiment=experiment,
                                         student_id=TEST_STUDENT_ID, track=track)
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track, url="www.google.com", open_as_tab=True)
        response = self.client.get(reverse("ab_testing_tool_deploy_intervention_point",
                                           args=(intervention_point.id,)), follow=True)
        self.assertTemplateUsed(response, "ab_tool/new_tab_redirect.html")
    
    def test_deploy_intervention_point_with_url_as_canvas_page(self):
        """ Tests deploy intervention_point successfully loads url in a window redirect"""
        self.set_roles([])
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        experiment.update(tracks_finalized=True)
        intervention_point = self.create_test_intervention_point()
        track = self.create_test_track()
        ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, experiment=experiment,
                                         student_id=TEST_STUDENT_ID, track=track)
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            track=track, url="www.google.com", is_canvas_page=True)
        response = self.client.get(reverse("ab_testing_tool_deploy_intervention_point",
                                           args=(intervention_point.id,)), follow=True)
        self.assertTemplateUsed(response, "ab_tool/window_redirect.html")
    
    def test_submit_create_intervention_point(self):
        """ Tests that create_intervention_point creates an InterventionPoint
            object verified by DB count """
        num_intervention_points = InterventionPoint.objects.count()
        data = {"name": "intervention_point", "notes": "hi"}
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        url = reverse("ab_testing_tool_submit_create_intervention_point", args=(experiment.id,))
        response = self.client.post(url, data, follow=True)
        self.assertOkay(response)
        self.assertEqual(num_intervention_points + 1, InterventionPoint.objects.count())
    
    def test_submit_create_intervention_point_with_intervention_pointurls(self):
        """ Tests that create_intervention_point creates an InterventionPoint
            object and InterventionPointUrl objects verified by DB count """
        intervention_point_name = "intervention_point"
        num_intervention_points = InterventionPoint.objects.count()
        num_intervention_pointurls = InterventionPointUrl.objects.count()
        track1 = self.create_test_track(name="t1")
        track2 = self.create_test_track(name="t2")
        data = {"name": intervention_point_name,
                STAGE_URL_TAG + str(track1.id): "http://example.com/page",
                STAGE_URL_TAG + str(track2.id): "http://example.com/otherpage",
                DEPLOY_OPTION_TAG + str(track1.id): "non_canvas_url",
                DEPLOY_OPTION_TAG + str(track2.id): "non_canvas_url",
                "notes": "hi"}
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        url = reverse("ab_testing_tool_submit_create_intervention_point", args=(experiment.id,))
        response = self.client.post(url, data, follow=True)
        self.assertOkay(response)
        self.assertEqual(num_intervention_points + 1, InterventionPoint.objects.count())
        self.assertEqual(num_intervention_pointurls + 2, InterventionPointUrl.objects.count())
        self.assertIsNotNone(InterventionPoint.objects.get(name=intervention_point_name))
        intervention_point = InterventionPoint.objects.get(name=intervention_point_name)
        self.assertIsNotNone(InterventionPointUrl.objects.get(
                intervention_point=intervention_point.id, track=track1.id))
        self.assertIsNotNone(InterventionPointUrl.objects.get(
                intervention_point=intervention_point.id, track=track2.id))
    
    def test_submit_create_intervention_point_unauthorized(self):
        """ Tests that create_intervention_point unauthorized """
        self.set_roles([])
        num_intervention_points = InterventionPoint.objects.count()
        num_intervention_pointurls = InterventionPointUrl.objects.count()
        data = {"name": "intervention_point",
                STAGE_URL_TAG + "1": "http://example.com/page",
                STAGE_URL_TAG + "2": "http://example.com/otherpage",
                "notes": "hi"}
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        url = reverse("ab_testing_tool_submit_create_intervention_point", args=(experiment.id,))
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(num_intervention_points, InterventionPoint.objects.count())
        self.assertEqual(num_intervention_pointurls, InterventionPointUrl.objects.count())
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_submit_edit_intervention_point(self):
        """ Tests that submit_edit_intervention_point does not change DB count
            but does change InterventionPoint attribute """
        intervention_point = self.create_test_intervention_point(name="old_name")
        intervention_point_id = intervention_point.id
        num_intervention_points = InterventionPoint.objects.count()
        data = {"name": "new_name",
                "notes": ""}
        response = self.client.post(
                reverse("ab_testing_tool_submit_edit_intervention_point", args=(intervention_point_id,)),
                data, follow=True)
        self.assertOkay(response)
        self.assertEqual(num_intervention_points, InterventionPoint.objects.count())
        intervention_point = InterventionPoint.objects.get(id=intervention_point_id)
        self.assertEqual(intervention_point.name, "new_name")
    
    def test_submit_edit_intervention_point_with_intervention_point_urls(self):
        """ Tests that submit_edit_intervention_point does not change DB count
            but does change InterventionPoint attribute, edits the existing
            InterventionPointUrl, and creates a new InterventionPointUrl """
        intervention_point = self.create_test_intervention_point(name="old_name")
        intervention_point_id = intervention_point.id
        track1 = self.create_test_track(name="track1")
        track2 = self.create_test_track(name="track2")
        intervention_pointurl = InterventionPointUrl.objects.create(
                intervention_point=intervention_point, url="http://www.example.com", track=track1)
        num_intervention_points = InterventionPoint.objects.count()
        num_intervention_pointurls = InterventionPointUrl.objects.count()
        data = {"name": "new_name",
                STAGE_URL_TAG + str(track1.id): "http://example.com/new_page",
                STAGE_URL_TAG + str(track2.id): "http://example.com/second_page",
                DEPLOY_OPTION_TAG + str(track1.id): "canvasPage",
                DEPLOY_OPTION_TAG + str(track2.id): "externalPage",
                "notes": "hi",
                "id": intervention_point_id}
        response = self.client.post(reverse("ab_testing_tool_submit_edit_intervention_point",
                                            args=(intervention_point_id,)), data, follow=True)
        self.assertOkay(response)
        self.assertEqual(num_intervention_points, InterventionPoint.objects.count())
        intervention_point = InterventionPoint.objects.get(id=intervention_point_id)
        new_num_intervention_pointurls = InterventionPointUrl.objects.count()
        self.assertEqual(intervention_point.name, "new_name")
        self.assertEqual(InterventionPointUrl.objects.get(
                pk=intervention_pointurl.id).url, "http://example.com/new_page")
        self.assertEqual(num_intervention_pointurls + 1, new_num_intervention_pointurls)
        self.assertEqual(InterventionPointUrl.objects.get(
                intervention_point=intervention_point, track=track2).url,
                "http://example.com/second_page")
    
    def test_submit_edit_intervention_point_unauthorized(self):
        """ Tests that submit_edit_intervention_point when unauthorized """
        self.set_roles([])
        intervention_point = self.create_test_intervention_point(name="old_name")
        num_intervention_points = InterventionPoint.objects.count()
        data = {"name": "new_name",
                "notes": "new notes"}
        response = self.client.post(
                reverse("ab_testing_tool_submit_edit_intervention_point", args=(intervention_point.id,)),
                data, follow=True)
        self.assertEqual(num_intervention_points, InterventionPoint.objects.count())
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_submit_edit_intervention_point_nonexistent(self):
        """ Tests that submit_edit_intervention_point method raises error for
            non-existent InterventionPoint """
        intervention_point_id = NONEXISTENT_STAGE_ID
        data = {"name": "new_name",
                "notes": "hi"}
        response = self.client.post(
                reverse("ab_testing_tool_submit_edit_intervention_point", args=(intervention_point_id,)),
                data, follow=True)
        self.assertEqual(response.status_code, 404)
    
    def test_submit_edit_intervention_point_wrong_course(self):
        """ Tests that submit_edit_intervention_point method raises error for
            existent InterventionPoint but for wrong course """
        intervention_point = self.create_test_intervention_point(
                name="old_name", course_id=TEST_OTHER_COURSE_ID)
        data = {"name": "new_name",
                "notes": "hi"}
        response = self.client.post(
                reverse("ab_testing_tool_submit_edit_intervention_point", args=(intervention_point.id,)),
                data, follow=True)
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_deploy_intervention_point_view(self):
        """ Tests deploy intervention_point  """
        intervention_point = self.create_test_intervention_point()
        track = self.create_test_track()
        InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            url="http://www.example.com", track=track)
        response = self.client.get(reverse("ab_testing_tool_deploy_intervention_point",
                                           args=(intervention_point.id,)), follow=True)
        self.assertOkay(response)
    
    def test_delete_intervention_point(self):
        """ Tests that delete_intervention_point method properly deletes a
            intervention_point when authorized """
        first_num_intervention_points = InterventionPoint.objects.count()
        intervention_point = self.create_test_intervention_point()
        self.assertEqual(first_num_intervention_points + 1, InterventionPoint.objects.count())
        response = self.client.get(reverse("ab_testing_tool_delete_intervention_point",
                                           args=(intervention_point.id,)), follow=True)
        second_num_intervention_points = InterventionPoint.objects.count()
        self.assertOkay(response)
        self.assertEqual(first_num_intervention_points, second_num_intervention_points)
    
    def test_delete_intervention_point_unauthorized(self):
        """ Tests that delete_intervention_point method raises error when unauthorized """
        self.set_roles([])
        first_num_intervention_points = InterventionPoint.objects.count()
        intervention_point = self.create_test_intervention_point()
        response = self.client.get(reverse("ab_testing_tool_delete_intervention_point",
                                           args=(intervention_point.id,)), follow=True)
        second_num_intervention_points = InterventionPoint.objects.count()
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
        self.assertNotEqual(first_num_intervention_points, second_num_intervention_points)
    
    def test_delete_intervention_point_nonexistent(self):
        """ Tests that delete_intervention_point method raises error for
            non-existent InterventionPoint """
        first_num_intervention_points = InterventionPoint.objects.count()
        self.create_test_intervention_point()
        intervention_point_id = NONEXISTENT_STAGE_ID
        response = self.client.get(reverse("ab_testing_tool_delete_intervention_point",
                                           args=(intervention_point_id,)), follow=True)
        second_num_intervention_points = InterventionPoint.objects.count()
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(first_num_intervention_points, second_num_intervention_points)
    
    def test_delete_intervention_point_wrong_course(self):
        """ Tests that delete_intervention_point method raises error for existent
            InterventionPoint but for wrong course """
        first_num_intervention_points = InterventionPoint.objects.count()
        intervention_point = self.create_test_intervention_point(course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("ab_testing_tool_delete_intervention_point",
                                           args=(intervention_point.id,)), follow=True)
        second_num_intervention_points = InterventionPoint.objects.count()
        self.assertError(response, UNAUTHORIZED_ACCESS)
        self.assertNotEqual(first_num_intervention_points, second_num_intervention_points)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_delete_intervention_point_installed(self, _mock1):
        """ Tests that delete_intervention_point method when intervention_point is installed """
        first_num_intervention_points = InterventionPoint.objects.count()
        intervention_point = self.create_test_intervention_point()
        self.assertEqual(first_num_intervention_points + 1, InterventionPoint.objects.count())
        ret_val = [True]
        with patch("ab_tool.canvas.CanvasModules.intervention_point_is_installed",
                   return_value=ret_val):
            response = self.client.get(reverse("ab_testing_tool_delete_intervention_point",
                                               args=(intervention_point.id,)), follow=True)
            second_num_intervention_points = InterventionPoint.objects.count()
            self.assertNotEqual(first_num_intervention_points, second_num_intervention_points)
            self.assertError(response, DELETING_INSTALLED_STAGE)
    
    def test_modules_page_edit_intervention_point(self):
        """ Tests modules_page_edit_intervention_point for admins redirects to editInterventionPointFromCanvas """
        intervention_point = self.create_test_intervention_point()
        response = self.client.get(reverse("ab_testing_tool_modules_page_edit_intervention_point",
                                           args=(intervention_point.id,)))
        self.assertOkay(response)
        self.assertTemplateUsed(response, "ab_tool/edit_intervention_point_from_canvas.html")
    
    def test_modules_page_view_intervention_point(self):
        """ Tests that submit_edit_intervention_point does not change DB count
            but does change InterventionPoint attribute, edits the existing
            InterventionPointUrl, and creates a new InterventionPointUrl """
        intervention_point = self.create_test_intervention_point(name="old_name")
        intervention_point_id = intervention_point.id
        track1 = self.create_test_track(name="track1")
        self.create_test_track(name="track2")
        InterventionPointUrl.objects.create(
                intervention_point=intervention_point, url="http://www.example.com", track=track1)
        response = self.client.post(reverse("ab_testing_tool_modules_page_view_intervention_point",
                                            args=(intervention_point_id,)), follow=True)
        self.assertOkay(response)
        self.assertTemplateUsed(response, "ab_tool/view_intervention_point_from_canvas.html")
    
    def test_submit_edit_intervention_point_from_modules(self):
        """ Tests that test_submit_edit_intervention_point_from_modules does not change DB count
            but does change InterventionPoint attribute """
        intervention_point = self.create_test_intervention_point(name="old_name")
        intervention_point_id = intervention_point.id
        num_intervention_points = InterventionPoint.objects.count()
        data = {"name": "new_name",
                "notes": ""}
        response = self.client.post(
                reverse("ab_testing_tool_submit_edit_intervention_point_from_modules",
                        args=(intervention_point_id,)), data, follow=True)
        self.assertOkay(response)
        self.assertEqual(num_intervention_points, InterventionPoint.objects.count())
        intervention_point = InterventionPoint.objects.get(id=intervention_point_id)
        self.assertEqual(intervention_point.name, "new_name")
