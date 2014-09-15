from ab_testing_tool_app.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_STAGE_ID, NONEXISTENT_TRACK_ID)
from django.core.urlresolvers import reverse
from ab_testing_tool_app.models import Track, Stage, StageUrl
from ab_testing_tool_app.exceptions import COURSE_TRACKS_ALREADY_FINALIZED,\
    NO_TRACKS_FOR_COURSE, UNAUTHORIZED_ACCESS, MISSING_TRACK

class TestTrackPages(SessionTestCase):
    """ Tests related to Track and Track pages and methods """
    
    def test_create_track_view(self):
        """ Tests edit_track template renders for url 'create_track' """
        response = self.client.get(reverse("create_track"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_track.html")
    
    def test_create_track_view_unauthorized(self):
        """ Tests edit_track template does not render for url 'create_track'
            when unauthorized """
        self.set_roles([])
        response = self.client.get(reverse("create_track"), follow=True)
        self.assertTemplateNotUsed(response, "edit_track.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_track_view(self):
        """ Tests edit_track template renders when authenticated """
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("edit_track", args=(track.id,)))
        self.assertTemplateUsed(response, "edit_track.html")
    
    def test_edit_track_view_unauthorized(self):
        """ Tests edit_track template renders when unauthorized """
        self.set_roles([])
        track = Track.objects.create(name="track1")
        response = self.client.get(reverse("edit_track", args=(track.id,)),
                                   follow=True)
        self.assertTemplateNotUsed(response, "edit_track.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_track_view_wrong_course(self):
        """ Tests edit_track when attempting to access a track from a different course """
        track = Track.objects.create(name="track1", course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("edit_track", args=(track.id,)))
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_submit_create_track(self):
        """Tests that create_track creates a Track object verified by DB count"""
        num_tracks = Track.objects.count()
        data = {"name": "track", "notes": "hi"}
        response = self.client.post(reverse("submit_create_track"), data,
                                    follow=True)
        self.assertEquals(num_tracks + 1, Track.objects.count(), response)
    
    def test_submit_create_track_unauthorized(self):
        """Tests that create_track creates a Track object verified by DB count"""
        self.set_roles([])
        num_tracks = Track.objects.count()
        data = {"name": "track", "notes": "hi"}
        response = self.client.post(reverse("submit_create_track"), data,
                                    follow=True)
        self.assertEquals(num_tracks, Track.objects.count())
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_submit_edit_track_unauthorized(self):
        """ Tests submit_edit_track when unauthorized"""
        self.set_roles([])
        track = Track.objects.create(name="old_name", course_id=TEST_COURSE_ID)
        track_id = track.id
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": track_id}
        response = self.client.post(reverse("submit_edit_track"), data,
                                    follow=True)
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_submit_edit_track_nonexistent(self):
        """ Tests that submit_edit_track method raises error for non-existent Track """
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": NONEXISTENT_STAGE_ID}
        response = self.client.post(reverse("submit_edit_track"), data,
                                    follow=True)
        self.assertError(response, MISSING_TRACK)
    
    def test_delete_track_unauthorized(self):
        """ Tests that delete_track method raises error when unauthorized """
        self.set_roles([])
        track = Track.objects.create(name="testname", course_id=TEST_COURSE_ID)
        first_num_tracks = Track.objects.count()
        response = self.client.get(reverse("delete_track", args=(track.id,)),
                                   follow=True)
        second_num_tracks = Track.objects.count()
        self.assertTemplateUsed(response, "not_authorized.html")
        self.assertEqual(first_num_tracks, second_num_tracks)
    
    def test_delete_track_nonexistent(self):
        """ Tests that delete_track method raises error for non-existent Track """
        Track.objects.create(name="testname", course_id=TEST_COURSE_ID)
        t_id = NONEXISTENT_TRACK_ID
        first_num_tracks = Track.objects.count()
        response = self.client.get(reverse("delete_track", args=(t_id,)), follow=True)
        second_num_tracks = Track.objects.count()
        self.assertEqual(first_num_tracks, second_num_tracks)
        self.assertError(response, MISSING_TRACK)
