import csv
import logging
import traceback
from django.http.response import HttpResponse

from ab_tool.models import ExperimentStudent, InterventionPointDeployments
from ab_tool.exceptions import CSV_ERROR

logger = logging.getLogger(__name__)


def log_intervention_point_deployment(course_id, student, intervention_point,
                                      experiment):
    InterventionPointDeployments.objects.create(
            course_id=course_id, student=student,
            intervention_point=intervention_point,
            experiment=experiment,
    )


def csv_response_and_writer(file_title):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ("attachment; filename=%s" % file_title)
        return response, csv.writer(response)
    except ValueError as exception:
        logger.error(repr(exception))
        logger.error(traceback.format_exc())
        raise CSV_ERROR


def get_student_list_csv(experiment, file_title):
    response, writer = csv_response_and_writer(file_title)
    # Write headers to CSV file
    headers = ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track",
               "Timestamp Last Updated"]
    writer.writerow(headers)
    # Write data to CSV file
    for s in ExperimentStudent.objects.filter(experiment=experiment):
        row = [s.student_id, s.lis_person_sourcedid, s.experiment.name,
               s.track.name, s.updated_on]
        writer.writerow(row)
    return response


def get_intervention_point_deployment_csv(experiment, file_title):
    response, writer = csv_response_and_writer(file_title)
    # Write headers to CSV file
    headers = ["Student ID", "LIS Person Sourcedid", "Experiment", "Intervention Point",
               "Timestamp Encountered"]
    writer.writerow(headers)
    # Write data to CSV file
    for i in InterventionPointDeployments.objects.filter(experiment=experiment):
        row = [i.student.student_id, i.student.lis_person_sourcedid,
               i.intervention_point.experiment.name, i.intervention_point.name,
               i.created_on]
        writer.writerow(row)
    return response
