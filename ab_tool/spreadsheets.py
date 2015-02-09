import csv
import xlsxwriter
import StringIO
import xlrd
from django.http.response import HttpResponse

from ab_tool.models import (ExperimentStudent, InterventionPointInteraction)
from ab_tool.controllers import streamed_csv_response
from ab_tool.canvas import get_unassigned_students
from ab_tool.exceptions import INVALID_FILE_TYPE


def get_student_list_csv(experiment, file_title):
    def row_generator():
        yield ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track",
                   "Timestamp Last Updated"]
        for s in ExperimentStudent.objects.filter(experiment=experiment):
            yield [s.student_id, s.lis_person_sourcedid, s.experiment.name,
                   s.track.name, s.updated_on]
    return streamed_csv_response(row_generator(), file_title)


def get_intervention_point_interactions_csv(experiment, file_title):
    def row_generator():
        yield ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track",
                   "Intervention Point", "Intervention Point URL", "Timestamp Encountered"]
        for i in InterventionPointInteraction.objects.filter(experiment=experiment):
            yield [i.student.student_id, i.student.lis_person_sourcedid,
                   i.experiment.name, i.track.name,
                   i.intervention_point.name, i.url, i.created_on]
    return streamed_csv_response(row_generator(), file_title)


def get_track_selection_xlsx(request, experiment, file_title="test.xlsx"):
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0, 3, 20)
    headers = ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track"]
    worksheet.write_row(0, 0, headers)
    students = get_unassigned_students(request, experiment)
    # Row offsets of +1 below are to account for header
    for i, student in enumerate(students):
        row = [student, "", experiment.name, ""]
        worksheet.write_row(i + 1, 0, row)
    # Add drop-down with track names as the only valid options for the missing column
    track_names = [t.name for t in experiment.tracks.all()]
    worksheet.data_validation(1, 3, len(students) + 1, 3,
                              {'validate': 'list', 'source': track_names,})
    workbook.close()
    output.seek(0)
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response = HttpResponse(output.read(), content_type=content_type)
    response['Content-Disposition'] = ("attachment; filename=%s" % file_title)
    return response


def get_track_selection_csv(request, experiment, file_title="test.xlsx"):
    def row_generator():
        yield ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track"]
        # Write data to CSV file
        for student in get_unassigned_students(request, experiment):
            yield [student, "", experiment.name, ""]
    return streamed_csv_response(row_generator(), file_title)


def parse_uploaded_file(experiment, unassigned_students, input_spreadsheet, filename):
    """ This function parses an uploaded spreadsheet of student track assignments.
        It returns a dictionary `students`, mapping sis_ids to track
        names as well as a list of errors (in string form) encountered while
        parsing the spreadsheet.  If errors is empty, no errors were encountered. """
    students = {}
    errors = []
    track_names = {track.name: track for track in experiment.tracks.all()}
    if filename.endswith('.csv'):
        # Slice off row 1 to skip headers
        csvreader = csv.reader(input_spreadsheet.split("\n")[1:])
        for row_number, row in enumerate(csvreader):
            parse_row(row, row_number, experiment, track_names,
                      unassigned_students, students, errors)
    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        book = xlrd.open_workbook(file_contents=input_spreadsheet)
        sheet = book.sheet_by_index(0)
        # Start at 1 to skip headers
        for row_number in range(1, sheet.nrows):
            row = sheet.row_values(row_number)
            parse_row(row, row_number, experiment, track_names,
                      unassigned_students, students, errors)
    else:
        raise INVALID_FILE_TYPE
    return students, errors


def parse_row(row, row_number, experiment, tracks, unassigned_students, students, errors):
    """ The arguments `students` and `errors` are each data structures
        from `parse_uploaded_file` indented to be modified by this function.
        If an error is encountered in parsing the row, a string representing the
        error is appended to the list `errors`.  If there are no errors,
        an entry (sis_id -> track_name) should be added to the `students` dict """
    if len(row) < 4 or row[3] == "" or row[3] is None:
        errors.append("Row %s: missing track name" % (row_number))
    elif row[3] not in tracks:
        errors.append("Row %s: invalid track name '%s'" % (row_number, row[3]))
    elif row[2] != experiment.name:
        errors.append("Row %s: wrong experiment name '%s'" % (row_number, row[2]))
    elif row[0] not in unassigned_students:
        errors.append("Row %s: student '%s' not available for assignment" % (row_number, row[0]))
    else:
        students[row[0]] = tracks[row[3]]
