from django.core.urlresolvers import reverse
from mock import patch

from ab_tool.constants import STAGE_URL_TAG, DEPLOY_OPTION_TAG
from ab_tool.models import (InterventionPoint, InterventionPointUrl, Track, CourseStudent,
    CourseSettings)
from ab_tool.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_STAGE_ID, APIReturn, LIST_MODULES,
    TEST_STUDENT_ID)
from ab_tool.exceptions import (NO_URL_FOR_TRACK,
    COURSE_TRACKS_NOT_FINALIZED, UNAUTHORIZED_ACCESS,
    DELETING_INSTALLED_STAGE, NO_TRACKS_FOR_COURSE)


class TestInterventionPointPages(SessionTestCase):
    """ Tests related to InterventionPoint related pages and methods """
    def test_deploy_intervention_point_admin(self):
        """ Tests deploy intervention_point for admins redirects to edit intervention_point """
        intervention_point = InterventionPoint.objects.create(name="intervention_point1", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("ab:deploy_intervention_point", args=(intervention_point.id,)))
        self.assertRedirects(response, reverse("ab:modules_page_edit_intervention_point", args=(intervention_point.id,)))
    
    def test_deploy_intervention_point_student_not_finalized(self):
        """ Tests deploy intervention_point for student errors if tracks not finalized
            for the course """
        self.set_roles([])
        intervention_point = InterventionPoint.objects.create(name="intervention_point1")
        response = self.client.get(reverse("ab:deploy_intervention_point", args=(intervention_point.id,)))
        self.assertError(response, COURSE_TRACKS_NOT_FINALIZED)
    
    def test_deploy_intervention_point_no_tracks_error(self):
        """ Tests deploy intervention_point for student creates errors with no tracks """
        self.set_roles([])
        CourseSettings.set_finalized(TEST_COURSE_ID)
        intervention_point = InterventionPoint.objects.create(name="intervention_point1")
        response = self.client.get(reverse("ab:deploy_intervention_point", args=(intervention_point.id,)))
        self.assertError(response, NO_TRACKS_FOR_COURSE)
    
    def test_deploy_intervention_point_student_created(self):
        """ Tests deploy intervention_point for student creates student object and assigns
            track to that student object """
        self.set_roles([])
        CourseSettings.set_finalized(TEST_COURSE_ID)
        intervention_point = InterventionPoint.objects.create(name="intervention_point1")
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        students = CourseStudent.objects.filter(course_id=TEST_COURSE_ID,
                                               student_id=TEST_STUDENT_ID)
        self.assertEqual(students.count(), 0)
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track,
                                url="http://www.example.com")
        self.client.get(reverse("ab:deploy_intervention_point", args=(intervention_point.id,)))
        student = CourseStudent.objects.get(course_id=TEST_COURSE_ID,
                                            student_id=TEST_STUDENT_ID)
        self.assertEqual(student.track.name, "track1")
    
    def test_deploy_intervention_point_student_redirect(self):
        """ Tests deploy intervention_point for student redirects to the correct url """
        self.set_roles([])
        CourseSettings.set_finalized(TEST_COURSE_ID)
        intervention_point = InterventionPoint.objects.create(name="intervention_point1")
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        intervention_point2 = InterventionPoint.objects.create(name="intervention_point2")
        track2 = Track.objects.create(name="track2", course_id=TEST_COURSE_ID)
        CourseStudent.objects.create(course_id=TEST_COURSE_ID,
                               student_id=TEST_STUDENT_ID, track=track)
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track,
                                url="http://www.example.com")
        InterventionPointUrl.objects.create(intervention_point=intervention_point2, track=track2,
                                url="http://www.incorrect-domain.com")
        response = self.client.get(reverse("ab:deploy_intervention_point", args=(intervention_point.id,)))
        # Can't use assertRedirects because it is an external domain
        self.assertEqual(response._headers['location'],
                         ("Location", "http://www.example.com"))
        self.assertEqual(response.status_code, 302)
    
    def test_deploy_intervention_point_no_url(self):
        """ Tests depoloy intervention_point for student with no url errors """
        self.set_roles([])
        CourseSettings.set_finalized(TEST_COURSE_ID)
        intervention_point = InterventionPoint.objects.create(name="intervention_point1")
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        CourseStudent.objects.create(course_id=TEST_COURSE_ID,
                               student_id=TEST_STUDENT_ID, track=track)
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track, url="")
        response = self.client.get(reverse("ab:deploy_intervention_point", args=(intervention_point.id,)))
        self.assertError(response, NO_URL_FOR_TRACK)
    
    def test_create_intervention_point_view(self):
        """ Tests edit_intervention_point template renders for url 'create_intervention_point' when authenticated """
        response = self.client.get(reverse("ab:create_intervention_point"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_intervention_point.html")
    
    def test_create_intervention_point_view_unauthorized(self):
        """ Tests edit_intervention_point template does not render for url 'create_intervention_point' when unauthorized """
        self.set_roles([])
        response = self.client.get(reverse("ab:create_intervention_point"), follow=True)
        self.assertTemplateNotUsed(response, "edit_intervention_point.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_intervention_point_view(self):
        """ Tests edit_intervention_point template renders when authenticated """
        intervention_point = InterventionPoint.objects.create(name="intervention_point1", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("ab:edit_intervention_point", args=(intervention_point.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_intervention_point.html")
    
    def test_edit_intervention_point_view_unauthorized(self):
        """ Tests edit_intervention_point template renders when unauthorized """
        self.set_roles([])
        intervention_point = InterventionPoint.objects.create(name="intervention_point1")
        t_id = intervention_point.id
        response = self.client.get(reverse("ab:edit_intervention_point", args=(t_id,)), follow=True)
        self.assertTemplateNotUsed(response, "edit_intervention_point.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_intervention_point_view_nonexistent(self):
        """ Tests edit_intervention_point template renders when intervention_point does not exist """
        intervention_point_id = NONEXISTENT_STAGE_ID
        response = self.client.get(reverse("ab:edit_intervention_point", args=(intervention_point_id,)))
        self.assertEqual(response.status_code, 404)
    
    def test_edit_intervention_point_view_wrong_course(self):
        """ Tests edit_track when attempting to access a track from a different course """
        intervention_point = InterventionPoint.objects.create(name="intervention_point1", course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("ab:edit_intervention_point", args=(intervention_point.id,)))
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_submit_create_intervention_point(self):
        """ Tests that create_intervention_point creates a InterventionPoint object verified by DB count """
        num_intervention_points = InterventionPoint.objects.count()
        data = {"name": "intervention_point", "notes": "hi"}
        response = self.client.post(reverse("ab:submit_create_intervention_point"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_intervention_points + 1, InterventionPoint.objects.count())
    
    def test_submit_create_intervention_point_with_intervention_pointurls(self):
        """ Tests that create_intervention_point creates a InterventionPoint object and InterventionPointUrl objects
            verified by DB count """
        intervention_point_name = "intervention_point"
        num_intervention_points = InterventionPoint.objects.count()
        num_intervention_pointurls = InterventionPointUrl.objects.count()
        track1 = Track.objects.create(name="t1", course_id=TEST_COURSE_ID)
        track2 = Track.objects.create(name="t2", course_id=TEST_COURSE_ID)
        data = {"name": intervention_point_name,
                STAGE_URL_TAG + str(track1.id): "http://example.com/page",
                STAGE_URL_TAG + str(track2.id): "http://example.com/otherpage",
                DEPLOY_OPTION_TAG + str(track1.id): "non_canvas_url",
                DEPLOY_OPTION_TAG + str(track2.id): "non_canvas_url",
                "notes": "hi"}
        response = self.client.post(reverse("ab:submit_create_intervention_point"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_intervention_points + 1, InterventionPoint.objects.count())
        self.assertEqual(num_intervention_pointurls + 2, InterventionPointUrl.objects.count())
        self.assertIsNotNone(InterventionPoint.objects.get(name=intervention_point_name))
        intervention_point = InterventionPoint.objects.get(name=intervention_point_name)
        self.assertIsNotNone(InterventionPointUrl.objects.get(intervention_point=intervention_point.id, track=track1.id))
        self.assertIsNotNone(InterventionPointUrl.objects.get(intervention_point=intervention_point.id, track=track2.id))
    
    def test_submit_create_intervention_point_unauthorized(self):
        """ Tests that create_intervention_point unauthorized """
        self.set_roles([])
        num_intervention_points = InterventionPoint.objects.count()
        num_intervention_pointurls = InterventionPointUrl.objects.count()
        data = {"name": "intervention_point",
                STAGE_URL_TAG + "1": "http://example.com/page",
                STAGE_URL_TAG + "2": "http://example.com/otherpage",
                "notes": "hi"}
        response = self.client.post(reverse("ab:submit_create_intervention_point"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(num_intervention_points, InterventionPoint.objects.count())
        self.assertEqual(num_intervention_pointurls, InterventionPointUrl.objects.count())
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_intervention_point_view_with_intervention_pointurls(self):
        """ Tests edit_intervention_point template renders with InterventionPointUrls """
        intervention_point = InterventionPoint.objects.create(name="intervention_point1", course_id=TEST_COURSE_ID)
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        track2 = Track.objects.create(name="track2", course_id=TEST_COURSE_ID)
        intervention_pointurl = InterventionPointUrl.objects.create(intervention_point=intervention_point,
                                            url="http://www.example.com", track=track)
        response = self.client.get(reverse("ab:edit_intervention_point", args=(intervention_point.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_intervention_point.html")
        self.assertIn("tracks", response.context)
        self.assertEqual(set(response.context["tracks"]), set([(track,intervention_pointurl), (track2,None)]))
    
    def test_submit_edit_intervention_point(self):
        """ Tests that submit_edit_intervention_point does not change DB count but does change InterventionPoint
            attribute """
        intervention_point = InterventionPoint.objects.create(name="old_name",
                                             course_id=TEST_COURSE_ID)
        intervention_point_id = intervention_point.id
        num_intervention_points = InterventionPoint.objects.count()
        data = {"name": "new_name",
                "notes": ""}
        response = self.client.post(
                reverse("ab:submit_edit_intervention_point", args=(intervention_point_id,)), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_intervention_points, InterventionPoint.objects.count())
        intervention_point = InterventionPoint.objects.get(id=intervention_point_id)
        self.assertEqual(intervention_point.name, "new_name")
    
    def test_submit_edit_intervention_point_with_intervention_pointurls(self):
        """ Tests that submit_edit_intervention_point does not change DB count but does change InterventionPoint
            attribute, edits the existing InterventionPointUrl, and creates a new InterventionPointUrl"""
        intervention_point = InterventionPoint.objects.create(name="old_name", course_id=TEST_COURSE_ID)
        intervention_point_id = intervention_point.id
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        track2 = Track.objects.create(name="track2", course_id=TEST_COURSE_ID)
        intervention_pointurl = InterventionPointUrl.objects.create(intervention_point=intervention_point, url="http://www.example.com", track=track)
        num_intervention_points = InterventionPoint.objects.count()
        num_intervention_pointurls = InterventionPointUrl.objects.count()
        data = {"name": "new_name",
                STAGE_URL_TAG + str(track.id): "http://example.com/new_page",
                STAGE_URL_TAG + str(track2.id): "http://example.com/second_page",
                DEPLOY_OPTION_TAG + str(track.id): "non_canvas_url",
                DEPLOY_OPTION_TAG + str(track2.id): "non_canvas_url",
                "notes": "hi",
                "id": intervention_point_id}
        response = self.client.post(reverse("ab:submit_edit_intervention_point", args=(intervention_point_id,)), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_intervention_points, InterventionPoint.objects.count())
        intervention_point = InterventionPoint.objects.get(id=intervention_point_id)
        new_num_intervention_pointurls = InterventionPointUrl.objects.count()
        self.assertEqual(intervention_point.name, "new_name")
        self.assertEqual(InterventionPointUrl.objects.get(pk=intervention_pointurl.id).url, "http://example.com/new_page")
        self.assertEqual(num_intervention_pointurls + 1, new_num_intervention_pointurls)
        self.assertEqual(InterventionPointUrl.objects.get(intervention_point=intervention_point, track=track2).url,
                "http://example.com/second_page")
    
    def test_submit_edit_intervention_point_unauthorized(self):
        """ Tests that submit_edit_intervention_point when unauthorized """
        self.set_roles([])
        intervention_point = InterventionPoint.objects.create(name="old_name", course_id=TEST_COURSE_ID)
        num_intervention_points = InterventionPoint.objects.count()
        data = {"name": "new_name",
                "notes": "new notes"}
        response = self.client.post(
                reverse("ab:submit_edit_intervention_point", args=(intervention_point.id,)), data, follow=True)
        self.assertEqual(num_intervention_points, InterventionPoint.objects.count())
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_submit_edit_intervention_point_nonexistent(self):
        """ Tests that submit_edit_intervention_point method raises error for non-existent InterventionPoint """
        intervention_point_id = NONEXISTENT_STAGE_ID
        data = {"name": "new_name",
                "notes": "hi"}
        response = self.client.post(
                reverse("ab:submit_edit_intervention_point", args=(intervention_point_id,)), data, follow=True)
        self.assertEqual(response.status_code, 404)
    
    def test_submit_edit_intervention_point_wrong_course(self):
        """ Tests that submit_edit_intervention_point method raises error for existent InterventionPoint but
            for wrong course  """
        intervention_point = InterventionPoint.objects.create(name="old_name",
                                     course_id=TEST_OTHER_COURSE_ID)
        data = {"name": "new_name",
                "notes": "hi"}
        response = self.client.post(
                reverse("ab:submit_edit_intervention_point", args=(intervention_point.id,)), data, follow=True)
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_deploy_intervention_point_view(self):
        """ Tests deploy intervention_point  """
        intervention_point = InterventionPoint.objects.create(name="intervention_point1", course_id=TEST_COURSE_ID)
        track = Track.objects.create(name="track1")
        InterventionPointUrl.objects.create(intervention_point=intervention_point, url="http://www.example.com", track=track)
        response = self.client.get(reverse("ab:deploy_intervention_point", args=(intervention_point.id,)),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_intervention_point(self):
        """ Tests that delete_intervention_point method properly deletes a intervention_point when authorized """
        first_num_intervention_points = InterventionPoint.objects.count()
        intervention_point = InterventionPoint.objects.create(name="testname", course_id=TEST_COURSE_ID)
        self.assertEqual(first_num_intervention_points + 1, InterventionPoint.objects.count())
        response = self.client.get(reverse("ab:delete_intervention_point", args=(intervention_point.id,)),
                                   follow=True)
        second_num_intervention_points = InterventionPoint.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(first_num_intervention_points, second_num_intervention_points)
    
    def test_delete_intervention_point_unauthorized(self):
        """ Tests that delete_intervention_point method raises error when unauthorized """
        self.set_roles([])
        first_num_intervention_points = InterventionPoint.objects.count()
        intervention_point = InterventionPoint.objects.create(name="testname", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("ab:delete_intervention_point", args=(intervention_point.id,)),
                                   follow=True)
        second_num_intervention_points = InterventionPoint.objects.count()
        self.assertTemplateUsed(response, "not_authorized.html")
        self.assertNotEqual(first_num_intervention_points, second_num_intervention_points)
    
    def test_delete_intervention_point_nonexistent(self):
        """ Tests that delete_intervention_point method raises error for non-existent InterventionPoint """
        first_num_intervention_points = InterventionPoint.objects.count()
        InterventionPoint.objects.create(name="testname", course_id=TEST_COURSE_ID)
        intervention_point_id = NONEXISTENT_STAGE_ID
        response = self.client.get(reverse("ab:delete_intervention_point", args=(intervention_point_id,)),
                                   follow=True)
        second_num_intervention_points = InterventionPoint.objects.count()
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(first_num_intervention_points, second_num_intervention_points)
    
    def test_delete_intervention_point_wrong_course(self):
        """ Tests that delete_intervention_point method raises error for existent InterventionPoint but for
            wrong course  """
        first_num_intervention_points = InterventionPoint.objects.count()
        intervention_point = InterventionPoint.objects.create(name="testname", course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("ab:delete_intervention_point", args=(intervention_point.id,)),
                                   follow=True)
        second_num_intervention_points = InterventionPoint.objects.count()
        self.assertError(response, UNAUTHORIZED_ACCESS)
        self.assertNotEqual(first_num_intervention_points, second_num_intervention_points)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_delete_intervention_point_installed(self, _mock1):
        """ Tests that delete_intervention_point method when intervention_point is installed """
        first_num_intervention_points = InterventionPoint.objects.count()
        intervention_point = InterventionPoint.objects.create(name="testname", course_id=TEST_COURSE_ID)
        self.assertEqual(first_num_intervention_points + 1, InterventionPoint.objects.count())
        ret_val = [True]
        with patch("ab_tool.views.intervention_point_pages.intervention_point_is_installed",
                   return_value=ret_val):
            response = self.client.get(reverse("ab:delete_intervention_point", args=(intervention_point.id,)),
                                       follow=True)
            second_num_intervention_points = InterventionPoint.objects.count()
            self.assertNotEqual(first_num_intervention_points, second_num_intervention_points)
            self.assertError(response, DELETING_INSTALLED_STAGE)