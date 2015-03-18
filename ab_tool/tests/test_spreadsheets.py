from ab_tool.tests.common import (SessionTestCase, APIReturn,
    LIST_MODULES, LIST_ITEMS, TEST_COURSE_ID, TEST_OTHER_COURSE_ID)

from ab_tool.spreadsheets import (get_student_list_csv, get_intervention_point_interactions_csv,
                                  get_track_selection_xlsx, get_track_selection_csv, parse_uploaded_file, parse_row)

from ab_tool.models import (InterventionPoint, InterventionPointUrl,
    ExperimentStudent, Experiment, InterventionPointInteraction)

from ab_tool.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_INTERVENTION_POINT_ID, APIReturn, LIST_MODULES,
    TEST_STUDENT_ID)

from ab_tool.exceptions import (MISSING_LTI_LAUNCH, MISSING_LTI_PARAM,
    NO_SDK_RESPONSE)

from mock import patch, MagicMock, ANY
from django_canvas_oauth.exceptions import NewTokenNeeded

from canvas_sdk.exceptions import CanvasAPIError

import re

TEST_FILE_TITLE = "test.xslx"

class TestSpreadsheets(SessionTestCase):

    def setUp(self):


        self.experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.experiment.update(tracks_finalized=True)
        self.intervention_point = self.create_test_intervention_point(name="intervention_point1", experiment=self.experiment)
        self.track1 = self.create_test_track(name="track1", experiment=self.experiment)
        self.intervention_point2 = self.create_test_intervention_point(name="intervention_point2", experiment=self.experiment)
        self.track2 = self.create_test_track(name="track2", experiment=self.experiment)



        self.student = ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, experiment=self.experiment,
                                         student_id=TEST_STUDENT_ID, track=self.track1)

        InterventionPointUrl.objects.create(intervention_point=self.intervention_point, track=self.track1,
                                            url="http://www.example.com")

        InterventionPointUrl.objects.create(intervention_point=self.intervention_point2, track=self.track2,
                                            url="http://www.incorrect-domain.com")

        #self.student = ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, student_id=TEST_STUDENT_ID,
        #                                 track=self.track1, experiment=self.experiment)
        #self.intervention_point = self.create_test_intervention_point(course_id=TEST_COURSE_ID)

        InterventionPointInteraction.objects.create(course_id=TEST_COURSE_ID, student=self.student,
                    intervention_point=self.intervention_point, experiment=self.experiment,
                    track=self.track1, url="http://example.com")

        # InterventionPointInteraction.objects.create(course_id=TEST_COURSE_ID, student=self.student,
        #             intervention_point=self.intervention_point, experiment=self.experiment,
        #             track=self.track2, url="http://example.com")



    def mock_api_exception(self):
        exception = CanvasAPIError()
        exception.response = MagicMock()
        return exception

    def mock_unauthorized_exception(self):
        exception = CanvasAPIError()
        exception.response = MagicMock()
        exception.status_code = 401
        return exception

    def test_get_student_list_csv(self):
        response = get_student_list_csv(self.experiment, TEST_FILE_TITLE)
        streaming_list = list(response.streaming_content)
        self.assertTrue(streaming_list[1].find(TEST_STUDENT_ID) > 0, "TEST_STUDENT_ID not in response")
        self.assertEqual(streaming_list, [ANY, ANY])

    def test_get_intervention_point_interactions_csv(self):
        response = get_intervention_point_interactions_csv(self.experiment, TEST_FILE_TITLE)
        streaming_list = list(response.streaming_content)
        self.assertTrue(streaming_list[1].find(TEST_STUDENT_ID) > 0, "TEST_STUDENT_ID not in response")
        self.assertEqual(streaming_list, [ANY, ANY])

    def test_get_track_selection_xlsx(self):
        self.assertTrue(True)

    def test_get_track_selection_csv(self):
        self.assertTrue(True)

    def test_parse_uploaded_file(self):
        self.assertTrue(True)

    def test_parse_row(self):
        self.assertTrue(True)
