from django.core.urlresolvers import reverse
from mock import patch

from ab_testing_tool_app.constants import STAGE_URL_TAG, DEPLOY_OPTION_TAG
from ab_testing_tool_app.models import (Stage, StageUrl, Track, CourseStudent,
    CourseSettings)
from ab_testing_tool_app.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_STAGE_ID, APIReturn, LIST_MODULES,
    TEST_STUDENT_ID)
from ab_testing_tool_app.exceptions import (NO_URL_FOR_TRACK,
    COURSE_TRACKS_NOT_FINALIZED, MISSING_STAGE, UNAUTHORIZED_ACCESS,
    DELETING_INSTALLED_STAGE, NO_TRACKS_FOR_COURSE)


class TestStagePages(SessionTestCase):
    """ Tests related to Stages and Stage-related pages and methods """
    def test_deploy_stage_admin(self):
        """ Tests deploy stage for admins redirects to edit stage """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("deploy_stage", args=(stage.id,)))
        self.assertRedirects(response, reverse("edit_stage", args=(stage.id,)))
    
    def test_deploy_stage_student_not_finalized(self):
        """ Tests deploy stage for student errors if tracks not finalized
            for the course """
        self.set_roles([])
        stage = Stage.objects.create(name="stage1")
        response = self.client.get(reverse("deploy_stage", args=(stage.id,)))
        self.assertError(response, COURSE_TRACKS_NOT_FINALIZED)
    
    def test_deploy_stage_no_tracks_error(self):
        """ Tests deploy stage for student creates errors with no tracks """
        self.set_roles([])
        CourseSettings.set_finalized(TEST_COURSE_ID)
        stage = Stage.objects.create(name="stage1")
        response = self.client.get(reverse("deploy_stage", args=(stage.id,)))
        self.assertError(response, NO_TRACKS_FOR_COURSE)
    
    def test_deploy_stage_student_created(self):
        """ Tests deploy stage for student creates student object and assigns
            track to that student object """
        self.set_roles([])
        CourseSettings.set_finalized(TEST_COURSE_ID)
        stage = Stage.objects.create(name="stage1")
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        student = CourseStudent.get_or_none(course_id=TEST_COURSE_ID,
                                      student_id=TEST_STUDENT_ID)
        self.assertEqual(student, None)
        StageUrl.objects.create(stage=stage, track=track,
                                url="http://www.example.com")
        self.client.get(reverse("deploy_stage", args=(stage.id,)))
        student = CourseStudent.get_or_none(course_id=TEST_COURSE_ID,
                                      student_id=TEST_STUDENT_ID)
        self.assertNotEqual(None, student)
        self.assertEqual(student.track.name, "track1")
    
    def test_deploy_stage_student_redirect(self):
        """ Tests deploy stage for student redirects to the correct url """
        self.set_roles([])
        CourseSettings.set_finalized(TEST_COURSE_ID)
        stage = Stage.objects.create(name="stage1")
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        stage2 = Stage.objects.create(name="stage2")
        track2 = Track.objects.create(name="track2", course_id=TEST_COURSE_ID)
        CourseStudent.objects.create(course_id=TEST_COURSE_ID,
                               student_id=TEST_STUDENT_ID, track=track)
        StageUrl.objects.create(stage=stage, track=track,
                                url="http://www.example.com")
        StageUrl.objects.create(stage=stage2, track=track2,
                                url="http://www.incorrect-domain.com")
        response = self.client.get(reverse("deploy_stage", args=(stage.id,)))
        # Can't use assertRedirects because it is an external domain
        self.assertEqual(response._headers['location'],
                         ("Location", "http://www.example.com"))
        self.assertEqual(response.status_code, 302)
    
    def test_deploy_stage_no_url(self):
        """ Tests depoloy stage for student with no url errors """
        self.set_roles([])
        CourseSettings.set_finalized(TEST_COURSE_ID)
        stage = Stage.objects.create(name="stage1")
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        CourseStudent.objects.create(course_id=TEST_COURSE_ID,
                               student_id=TEST_STUDENT_ID, track=track)
        StageUrl.objects.create(stage=stage, track=track, url="")
        response = self.client.get(reverse("deploy_stage", args=(stage.id,)))
        self.assertError(response, NO_URL_FOR_TRACK)
    
    def test_create_stage_view(self):
        """ Tests edit_stage template renders for url 'create_stage' when authenticated """
        response = self.client.get(reverse("create_stage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")
    
    def test_create_stage_view_unauthorized(self):
        """ Tests edit_stage template does not render for url 'create_stage' when unauthorized """
        self.set_roles([])
        response = self.client.get(reverse("create_stage"), follow=True)
        self.assertTemplateNotUsed(response, "edit_stage.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_stage_view(self):
        """ Tests edit_stage template renders when authenticated """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("edit_stage", args=(stage.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")
    
    def test_edit_stage_view_unauthorized(self):
        """ Tests edit_stage template renders when unauthorized """
        self.set_roles([])
        stage = Stage.objects.create(name="stage1")
        t_id = stage.id
        response = self.client.get(reverse("edit_stage", args=(t_id,)), follow=True)
        self.assertTemplateNotUsed(response, "edit_stage.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_stage_view_nonexistent(self):
        """ Tests edit_stage template renders when stage does not exist """
        stage_id = NONEXISTENT_STAGE_ID
        response = self.client.get(reverse("edit_stage", args=(stage_id,)))
        self.assertError(response, MISSING_STAGE)
    
    def test_edit_stage_view_wrong_course(self):
        """ Tests edit_track when attempting to access a track from a different course """
        stage = Stage.objects.create(name="stage1", course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("edit_stage", args=(stage.id,)))
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_submit_create_stage(self):
        """ Tests that create_stage creates a Stage object verified by DB count """
        num_stages = Stage.objects.count()
        data = {"name": "stage", "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_stages + 1, Stage.objects.count())
    
    def test_submit_create_stage_with_stageurls(self):
        """ Tests that create_stage creates a Stage object and StageUrl objects
            verified by DB count """
        stage_name = "stage"
        num_stages = Stage.objects.count()
        num_stageurls = StageUrl.objects.count()
        track1 = Track.objects.create(name="t1", course_id=TEST_COURSE_ID)
        track2 = Track.objects.create(name="t2", course_id=TEST_COURSE_ID)
        data = {"name": stage_name,
                STAGE_URL_TAG + str(track1.id): "http://example.com/page",
                STAGE_URL_TAG + str(track2.id): "http://example.com/otherpage",
                DEPLOY_OPTION_TAG + str(track1.id): "non_canvas_url",
                DEPLOY_OPTION_TAG + str(track2.id): "non_canvas_url",
                "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_stages + 1, Stage.objects.count())
        self.assertEqual(num_stageurls + 2, StageUrl.objects.count())
        self.assertIsNotNone(Stage.objects.get(name=stage_name))
        stage = Stage.objects.get(name=stage_name)
        self.assertIsNotNone(StageUrl.objects.get(stage=stage.id, track=track1.id))
        self.assertIsNotNone(StageUrl.objects.get(stage=stage.id, track=track2.id))
    
    def test_submit_create_stage_unauthorized(self):
        """ Tests that create_stage unauthorized """
        self.set_roles([])
        num_stages = Stage.objects.count()
        num_stageurls = StageUrl.objects.count()
        data = {"name": "stage",
                STAGE_URL_TAG + "1": "http://example.com/page",
                STAGE_URL_TAG + "2": "http://example.com/otherpage",
                "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(num_stages, Stage.objects.count())
        self.assertEqual(num_stageurls, StageUrl.objects.count())
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_stage_view_with_stageurls(self):
        """ Tests edit_stage template renders with StageUrls """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        track2 = Track.objects.create(name="track2", course_id=TEST_COURSE_ID)
        stageurl = StageUrl.objects.create(stage=stage, url="http://www.example.com", track=track)
        response = self.client.get(reverse("edit_stage", args=(stage.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")
        self.assertIn("tracks", response.context)
        self.assertEqual(set(response.context["tracks"]), set([(track,stageurl), (track2,None)]))
    
    def test_submit_edit_stage(self):
        """ Tests that submit_edit_stage does not change DB count but does change Stage
            attribute """
        stage = Stage.objects.create(name="old_name",
                                             course_id=TEST_COURSE_ID)
        stage_id = stage.id
        num_stages = Stage.objects.count()
        data = {"name": "new_name",
                "notes": "",
                "id": stage_id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_stages, Stage.objects.count())
        stage = Stage.objects.get(id=stage_id)
        self.assertEqual(stage.name, "new_name")
    
    def test_submit_edit_stage_with_stageurls(self):
        """ Tests that submit_edit_stage does not change DB count but does change Stage
            attribute, edits the existing StageUrl, and creates a new StageUrl"""
        stage = Stage.objects.create(name="old_name", course_id=TEST_COURSE_ID)
        stage_id = stage.id
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        track2 = Track.objects.create(name="track2", course_id=TEST_COURSE_ID)
        stageurl = StageUrl.objects.create(stage=stage, url="http://www.example.com", track=track)
        num_stages = Stage.objects.count()
        num_stageurls = StageUrl.objects.count()
        data = {"name": "new_name",
                STAGE_URL_TAG + str(track.id): "http://example.com/new_page",
                STAGE_URL_TAG + str(track2.id): "http://example.com/second_page",
                DEPLOY_OPTION_TAG + str(track.id): "non_canvas_url",
                DEPLOY_OPTION_TAG + str(track2.id): "non_canvas_url",
                "notes": "hi",
                "id": stage_id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_stages, Stage.objects.count())
        stage = Stage.objects.get(id=stage_id)
        new_num_stageurls = StageUrl.objects.count()
        self.assertEqual(stage.name, "new_name")
        self.assertEqual(StageUrl.objects.get(pk=stageurl.id).url, "http://example.com/new_page")
        self.assertEqual(num_stageurls + 1, new_num_stageurls)
        self.assertEqual(StageUrl.objects.get(stage=stage, track=track2).url,
                "http://example.com/second_page")
    
    def test_submit_edit_stage_unauthorized(self):
        """ Tests that submit_edit_stage when unauthorized """
        self.set_roles([])
        stage = Stage.objects.create(name="old_name",
                                             course_id=TEST_COURSE_ID)
        stage_id = stage.id
        num_stages = Stage.objects.count()
        data = {"name": "new_name",
                "notes": "new notes",
                "id": stage_id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertEqual(num_stages, Stage.objects.count())
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_submit_edit_stage_nonexistent(self):
        """ Tests that submit_edit_stage method raises error for non-existent Stage """
        data = {"name": "new_name",
                "notes": "hi",
                "id": NONEXISTENT_STAGE_ID}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertError(response, MISSING_STAGE)
    
    def test_submit_edit_stage_wrong_course(self):
        """ Tests that submit_edit_stage method raises error for existent Stage but
            for wrong course  """
        stage = Stage.objects.create(name="old_name",
                                     course_id=TEST_OTHER_COURSE_ID)
        data = {"name": "new_name",
                "notes": "hi",
                "id": stage.id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_deploy_stage_view(self):
        """ Tests deploy stage  """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        track = Track.objects.create(name="track1")
        StageUrl.objects.create(stage=stage, url="http://www.example.com", track=track)
        response = self.client.get(reverse("deploy_stage", args=(stage.id,)),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_stage(self):
        """ Tests that delete_stage method properly deletes a stage when authorized """
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        self.assertEqual(first_num_stages + 1, Stage.objects.count())
        response = self.client.get(reverse("delete_stage", args=(stage.id,)),
                                   follow=True)
        second_num_stages = Stage.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(first_num_stages, second_num_stages)
    
    def test_delete_stage_unauthorized(self):
        """ Tests that delete_stage method raises error when unauthorized """
        self.set_roles([])
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("delete_stage", args=(stage.id,)),
                                   follow=True)
        second_num_stages = Stage.objects.count()
        self.assertTemplateUsed(response, "not_authorized.html")
        self.assertNotEqual(first_num_stages, second_num_stages)
    
    def test_delete_stage_nonexistent(self):
        """ Tests that delete_stage method raises error for non-existent Stage """
        first_num_stages = Stage.objects.count()
        Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        stage_id = NONEXISTENT_STAGE_ID
        response = self.client.get(reverse("delete_stage", args=(stage_id,)),
                                   follow=True)
        second_num_stages = Stage.objects.count()
        self.assertError(response, MISSING_STAGE)
        self.assertNotEqual(first_num_stages, second_num_stages)
    
    def test_delete_stage_wrong_course(self):
        """ Tests that delete_stage method raises error for existent Stage but for
            wrong course  """
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("delete_stage", args=(stage.id,)),
                                   follow=True)
        second_num_stages = Stage.objects.count()
        self.assertError(response, UNAUTHORIZED_ACCESS)
        self.assertNotEqual(first_num_stages, second_num_stages)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_delete_stage_installed(self, _mock1):
        """ Tests that delete_stage method when stage is installed """
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        self.assertEqual(first_num_stages + 1, Stage.objects.count())
        ret_val = [True]
        with patch("ab_testing_tool_app.views.stage_pages.stage_is_installed",
                   return_value=ret_val):
            response = self.client.get(reverse("delete_stage", args=(stage.id,)),
                                       follow=True)
            second_num_stages = Stage.objects.count()
            self.assertNotEqual(first_num_stages, second_num_stages)
            self.assertError(response, DELETING_INSTALLED_STAGE)
