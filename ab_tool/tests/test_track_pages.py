from ab_tool.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_TRACK_ID)
from django.core.urlresolvers import reverse
from ab_tool.models import Track, Experiment, InterventionPointUrl
from ab_tool.exceptions import (EXPERIMENT_TRACKS_ALREADY_FINALIZED,
    NO_TRACKS_FOR_EXPERIMENT, UNAUTHORIZED_ACCESS)

class TestTrackPages(SessionTestCase):
    """ Tests related to Track and Track pages and methods """
    
    def test_create_track_view(self):
        """ Tests edit_track template renders for url 'create_track' """
        response = self.client.get(reverse("ab:create_track"))
        self.assertOkay(response)
        self.assertTemplateUsed(response, "ab_tool/edit_track.html")
    
    def test_create_track_view_already_finalized(self):
        """ Tests that create track doesn't render when tracks are finalized """
        Experiment.get_placeholder_course_experiment(TEST_COURSE_ID).update(tracks_finalized=True)
        response = self.client.get(reverse("ab:create_track"))
        self.assertError(response, EXPERIMENT_TRACKS_ALREADY_FINALIZED)
    
    def test_create_track_view_unauthorized(self):
        """ Tests edit_track template does not render for url 'create_track'
            when unauthorized """
        self.set_roles([])
        response = self.client.get(reverse("ab:create_track"), follow=True)
        self.assertTemplateNotUsed(response, "ab_tool/edit_track.html")
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_edit_track_view(self):
        """ Tests edit_track template renders when authenticated """
        track = self.create_test_track()
        response = self.client.get(reverse("ab:edit_track", args=(track.id,)))
        self.assertTemplateUsed(response, "ab_tool/edit_track.html")
    
    def test_edit_track_view_unauthorized(self):
        """ Tests edit_track template renders when unauthorized """
        self.set_roles([])
        track = self.create_test_track(course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("ab:edit_track", args=(track.id,)),
                                   follow=True)
        self.assertTemplateNotUsed(response, "ab_tool/edit_track.html")
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_edit_track_view_nonexistent(self):
        """Tests edit_track when track does not exist"""
        t_id = NONEXISTENT_TRACK_ID
        response = self.client.get(reverse("ab:edit_track", args=(t_id,)))
        self.assertTemplateNotUsed(response, "ab_tool/edit_track.html")
        self.assertEquals(response.status_code, 404)
    
    def test_edit_track_view_wrong_course(self):
        """ Tests edit_track when attempting to access a track from a different course """
        track = self.create_test_track(course_id=TEST_OTHER_COURSE_ID)
        response = self.client.get(reverse("ab:edit_track", args=(track.id,)))
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_submit_create_track(self):
        """Tests that create_track creates a Track object verified by DB count"""
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        num_tracks = Track.objects.count()
        data = {"name": "track", "notes": "hi"}
        response = self.client.post(reverse("ab:submit_create_track"),
                                    data, follow=True)
        self.assertEquals(num_tracks + 1, Track.objects.count(), response)
    
    def test_submit_create_track_already_finalized(self):
        """ Tests that submit create track doesn't work when tracks are finalized """
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        experiment.update(tracks_finalized=True)
        response = self.client.get(reverse("ab:submit_create_track"))
        self.assertError(response, EXPERIMENT_TRACKS_ALREADY_FINALIZED)
    
    def test_submit_create_track_unauthorized(self):
        """Tests that create_track creates a Track object verified by DB count"""
        self.set_roles([])
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        num_tracks = Track.objects.count()
        data = {"name": "track", "notes": "hi"}
        response = self.client.post(reverse("ab:submit_create_track"),
                                    data, follow=True)
        self.assertEquals(num_tracks, Track.objects.count())
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_submit_edit_track(self):
        """ Tests that submit_edit_track does not change DB count but does change Track
            attribute"""
        track = self.create_test_track(name="old_name")
        track_id = track.id
        num_tracks = Track.objects.count()
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": ""}
        response = self.client.post(
                reverse("ab:submit_edit_track", args=(track_id,)), data, follow=True)
        self.assertOkay(response)
        self.assertEquals(num_tracks, Track.objects.count())
        track = Track.objects.get(id=track_id)
        self.assertEquals(track.name, "new_name")
    
    def test_submit_edit_track_unauthorized(self):
        """ Tests submit_edit_track when unauthorized"""
        self.set_roles([])
        track = self.create_test_track(name="old_name")
        track_id = track.id
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": ""}
        response = self.client.post(
                reverse("ab:submit_edit_track", args=(track_id,)), data, follow=True)
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_submit_edit_track_nonexistent(self):
        """ Tests that submit_edit_track method raises error for non-existent Track """
        track_id = NONEXISTENT_TRACK_ID
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": ""}
        response = self.client.post(
                reverse("ab:submit_edit_track", args=(track_id,)), data, follow=True)
        self.assertEquals(response.status_code, 404)
    
    def test_submit_edit_track_wrong_course(self):
        """ Tests that submit_edit_track method raises error for existent Track but
            for wrong course"""
        track = self.create_test_track(name="old_name",
                                       course_id=TEST_OTHER_COURSE_ID)
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": ""}
        response = self.client.post(
                reverse("ab:submit_edit_track", args=(track.id,)), data, follow=True)
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_delete_track(self):
        """ Tests that delete_track method properly deletes a track when authorized"""
        first_num_tracks = Track.objects.count()
        track = self.create_test_track()
        self.assertEqual(first_num_tracks + 1, Track.objects.count())
        response = self.client.get(reverse("ab:delete_track", args=(track.id,)),
                                   follow=True)
        second_num_tracks = Track.objects.count()
        self.assertOkay(response)
        self.assertEqual(first_num_tracks, second_num_tracks)
    
    def test_delete_track_already_finalized(self):
        """ Tests that delete track doesn't work when tracks are finalized """
        Experiment.get_placeholder_course_experiment(TEST_COURSE_ID).update(tracks_finalized=True)
        track = self.create_test_track()
        first_num_tracks = Track.objects.count()
        response = self.client.get(reverse("ab:delete_track", args=(track.id,)),
                                   follow=True)
        second_num_tracks = Track.objects.count()
        self.assertError(response, EXPERIMENT_TRACKS_ALREADY_FINALIZED)
        self.assertEqual(first_num_tracks, second_num_tracks)
    
    def test_delete_track_unauthorized(self):
        """ Tests that delete_track method raises error when unauthorized """
        self.set_roles([])
        track = self.create_test_track()
        first_num_tracks = Track.objects.count()
        response = self.client.get(reverse("ab:delete_track", args=(track.id,)),
                                   follow=True)
        second_num_tracks = Track.objects.count()
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
        self.assertEqual(first_num_tracks, second_num_tracks)
    
    def test_delete_track_nonexistent(self):
        """ Tests that delete_track method raises error for non-existent Track """
        self.create_test_track()
        t_id = NONEXISTENT_TRACK_ID
        first_num_tracks = Track.objects.count()
        response = self.client.get(reverse("ab:delete_track", args=(t_id,)), follow=True)
        second_num_tracks = Track.objects.count()
        self.assertEqual(first_num_tracks, second_num_tracks)
        self.assertEquals(response.status_code, 404)
    
    def test_delete_track_wrong_course(self):
        """ Tests that delete_track method raises error for existent Track but for
            wrong course """
        track = self.create_test_track(course_id=TEST_OTHER_COURSE_ID)
        first_num_tracks = Track.objects.count()
        response = self.client.get(reverse("ab:delete_track", args=(track.id,)),
                                   follow=True)
        second_num_tracks = Track.objects.count()
        self.assertEqual(first_num_tracks, second_num_tracks)
        self.assertError(response, UNAUTHORIZED_ACCESS)
    
    def test_delete_track_deletes_intervention_point_urls(self):
        """ Tests that intervention_point_urls of a track are deleted when the track is """
        track1 = self.create_test_track(name="track1")
        track2 = self.create_test_track(name="track2")
        intervention_point = self.create_test_intervention_point()
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track1, url="example.com")
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track2, url="example.com")
        first_num_intervention_point_urls = InterventionPointUrl.objects.count()
        response = self.client.get(reverse("ab:delete_track", args=(track1.id,)),
                                   follow=True)
        second_num_intervention_point_urls = InterventionPointUrl.objects.count()
        self.assertOkay(response)
        self.assertEqual(first_num_intervention_point_urls - 1, second_num_intervention_point_urls)
    
    def test_finalize_tracks(self):
        """ Tests that the finalize tracks page sets the appropriate course """
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertFalse(experiment.tracks_finalized)
        self.create_test_track()
        response = self.client.get(reverse("ab:finalize_tracks"),
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
        self.client.get(reverse("ab:finalize_tracks"),
                        follow=True)
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.assertFalse(experiment.tracks_finalized)
    
    def test_finalize_tracks_no_tracks(self):
        """ Tests that finalize fails if there are no tracks """
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        response = self.client.get(reverse("ab:finalize_tracks"),
                                   follow=True)
        self.assertError(response, NO_TRACKS_FOR_EXPERIMENT)
