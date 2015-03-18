
from ab_tool.spreadsheets import (get_student_list_csv, get_intervention_point_interactions_csv,
                                  get_track_selection_xlsx, get_track_selection_csv,
                                  parse_uploaded_file, parse_row)
from ab_tool.models import (InterventionPointUrl, ExperimentStudent, Experiment,
                            InterventionPointInteraction)

from ab_tool.tests.common import (SessionTestCase, TEST_COURSE_ID, TEST_STUDENT_ID)

from django.test import RequestFactory
from mock import patch, MagicMock, ANY, Mock
from error_middleware.exceptions import Renderable404

TEST_XLSX_FILE_NAME = "test.xlsx"
TEST_CSV_FILE_NAME = "test.csv"
TEST_DOMAIN = "example.com"
TEST_STUDENT_EMAIL = "student@example.com"
TEST_STUDENT_DICT = {'10123478' : 'Lisa',
                     '20123278' : 'Jan',
                     '34512278' : 'Pete',
                     '40212478' : 'Bob',
                     }
TEST_CONTENT_TYPE = [('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                     ('Content-Disposition', 'attachment; filename=test.xlsx')]
TEST_TRACK_SELECTION_RESPONSE = ['Student Name,Student ID,Experiment,Assigned Track\r\n',
                                 'Bob,40212478,Experiment 1,\r\n',
                                 'Jan,20123278,Experiment 1,\r\n',
                                 'Lisa,10123478,Experiment 1,\r\n',
                                 'Pete,34512278,Experiment 1,\r\n']


class TestSpreadsheets(SessionTestCase):

    def setUp(self):

        self.request = RequestFactory().get('/fake-path')
        self.request.user = Mock(name='user_mock')
        self.request.session = {   "oauth_return_uri": TEST_DOMAIN,
                                                "LTI_LAUNCH" : {
                                                     "custom_canvas_api_domain" : TEST_DOMAIN,
                                                     "lis_person_contact_email_primary" : TEST_STUDENT_EMAIL,
                                                     "custom_canvas_course_id" : TEST_COURSE_ID,
                                                     },
                                            }

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

        InterventionPointInteraction.objects.create(course_id=TEST_COURSE_ID, student=self.student,
                    intervention_point=self.intervention_point, experiment=self.experiment,
                    track=self.track1, url="http://example.com")


    def test_get_student_list_csv(self):
        """

        """
        response = get_student_list_csv(self.experiment, TEST_XLSX_FILE_NAME)
        streaming_list = list(response.streaming_content)
        self.assertTrue(TEST_STUDENT_ID in streaming_list[1])

    def test_get_intervention_point_interactions_csv(self):
        """

        """
        response = get_intervention_point_interactions_csv(self.experiment, TEST_XLSX_FILE_NAME)
        streaming_list = list(response.streaming_content)
        self.assertTrue(TEST_DOMAIN in streaming_list[1])

    @patch('ab_tool.spreadsheets.get_unassigned_students')
    def test_get_track_selection_xlsx(self, mock_get_unassigned_students):
        """

        """
        mock_get_unassigned_students.return_value = TEST_STUDENT_DICT
        response = get_track_selection_xlsx(self.request, self.experiment)
        self.assertEqual(response.items(), TEST_CONTENT_TYPE)

    @patch('ab_tool.spreadsheets.get_unassigned_students')
    def test_get_track_selection_csv(self, mock_get_unassigned_students):
        """

        """
        mock_get_unassigned_students.return_value = TEST_STUDENT_DICT
        response = get_track_selection_csv(self.request, self.experiment)
        streaming_list = list(response.streaming_content)
        self.assertEqual(streaming_list, TEST_TRACK_SELECTION_RESPONSE)

    @patch('ab_tool.spreadsheets.xlrd.open_workbook')
    def test_parse_uploaded_xlsx_file(self, mock_open_workbook):
        """

        """
        result = parse_uploaded_file(self.experiment, TEST_STUDENT_DICT, TEST_TRACK_SELECTION_RESPONSE, TEST_XLSX_FILE_NAME)
        mock_open_workbook.assert_called_with(file_contents=TEST_TRACK_SELECTION_RESPONSE)

    @patch('ab_tool.spreadsheets.csv.reader')
    def test_parse_uploaded_csv_file(self, mock_csv_reader):
        """

        """
        result = parse_uploaded_file(self.experiment, TEST_STUDENT_DICT,
                                     TEST_TRACK_SELECTION_RESPONSE[1], TEST_CSV_FILE_NAME)
        data = TEST_TRACK_SELECTION_RESPONSE[1].split("\n")[1:]
        mock_csv_reader.assert_called_with(data)

    @patch('ab_tool.spreadsheets.xlrd.open_workbook')
    def test_parse_uploaded_file_invalid_file_name(self, mock_open_workbook):
        """

        """
        self.assertRaises(Renderable404, parse_uploaded_file, self.experiment,
                          TEST_STUDENT_DICT, TEST_TRACK_SELECTION_RESPONSE, "test.xslx")

    def test_parse_row(self):
        """

        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        row = ['Jan','20123278','Experiment 1', 'track1']
        row_number = 1
        parse_row(row, row_number, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(students.keys(), ['20123278'])

    def test_parse_row_missing_track(self):
        """

        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        row = ['Jan','20123278','Experiment 1', ]
        row_number = 1
        parse_row(row, row_number, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(errors, ["Row 1: missing track name"])

    def test_parse_row_invalid_track_name(self):
        """

        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        row = ['Jan','20123278','Experiment 1', 'track3']
        row_number = 1
        parse_row(row, row_number, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(errors, ["Row 1: invalid track name 'track3'"])

    def test_parse_row_wrong_experiment_name(self):
        """

        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        row = ['Jan','20123278','Experiment 2', 'track2']
        row_number = 1
        parse_row(row, row_number, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(errors, ["Row 1: wrong experiment name 'Experiment 2'"])

    def test_parse_row_student_not_available_for_assignment(self):
        """

        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        row = ['Fred','50123278','Experiment 1', 'track2']
        row_number = 1
        parse_row(row, row_number, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(errors, ["Row 1: student 'Fred' not available for assignment"])

