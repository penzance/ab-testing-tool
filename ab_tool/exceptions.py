from error_middleware.exceptions import (Renderable500, Renderable400,
    Renderable403, Renderable404)
from django.conf import settings

class NoValidCredentials(Exception): pass

UNAUTHORIZED_ACCESS = Renderable403("Sorry, you do not have access to this course. If you feel that this is an error, please contact a member of your local academic support staff.")

#The following error message is displayed to end users (e.g. instructors)
ADMIN_VISIBLE_ERROR = """Sadly, there was a problem loading this page. Please try again.
 If the problem persists please notify your local academic support staff."""
NO_SDK_RESPONSE = Renderable500(ADMIN_VISIBLE_ERROR)
MISSING_LTI_LAUNCH = Renderable400(ADMIN_VISIBLE_ERROR)
MISSING_LTI_PARAM = Renderable400(ADMIN_VISIBLE_ERROR)
BAD_INTERVENTION_POINT_ID = Renderable400(ADMIN_VISIBLE_ERROR)
MISSING_RETURN_TYPES_PARAM = Renderable400(ADMIN_VISIBLE_ERROR)
MISSING_RETURN_URL = Renderable400(ADMIN_VISIBLE_ERROR)

#Error messages for forbidden deletion
DELETING_INSTALLED_STAGE = Renderable400("Deleting an installed Intervention Point is not allowed")

UNAUTHORIZED_ACCESS = Renderable403("You do not have access to this course.")

FILE_TOO_LARGE = Renderable403("Files over %sMB are not allowed for upload" %
                               (int(settings.MAX_FILE_UPLOAD_SIZE) / 1024 / 1024))

MISSING_RETURN_TYPES_PARAM = Renderable400("Invalid ext_content_return_types")

MISSING_RETURN_URL = Renderable400("No ext_content_return_url")

DELETING_INSTALLED_INTERVENTION_POINT = Renderable400("Deleting an installed Intervention Point is not allowed.")
DELETING_INTERVENTION_POINT_AFTER_FINALIZED = Renderable400("Deleting an Intervention Point is not allowed after its experiment has been started.")
EXPERIMENT_TRACKS_ALREADY_FINALIZED = Renderable400("You can't edit or delete the experiment after it has been started.")
INTERVENTION_POINTS_ARE_INSTALLED = Renderable400("You can't edit or delete the experiment if there are intervention points installed for the experiment.")

#The following message is displayed to users e.g. students when there doens't exist content accessible to them
STUDENT_VISIBLE_ERROR = """It appears that you don't have permission to access this page.
Please make sure you're authorized to view this content.
If you think you should be able to view this page, please contact a member of your teaching staff."""
EXPERIMENT_TRACKS_NOT_FINALIZED = Renderable403(STUDENT_VISIBLE_ERROR)
NO_URL_FOR_TRACK = Renderable403(STUDENT_VISIBLE_ERROR)
NO_TRACKS_FOR_EXPERIMENT = Renderable403(STUDENT_VISIBLE_ERROR)
CSV_UPLOAD_NEEDED = Renderable403(STUDENT_VISIBLE_ERROR)
TRACK_WEIGHTS_NOT_SET = Renderable403(STUDENT_VISIBLE_ERROR)

INPUT_NOT_ALLOWED = Renderable404("Input does not follow requirements")
INVALID_FILE_TYPE = Renderable404("File type must be csv, xls, or xlsx")

#Human-readable error messages for specific exceptions

MISSING_NAME_PARAM = Renderable400("Names are required. Please go back and submit a name for all experiments, tracks, and intervention points.")
INCORRECT_WEIGHTING_PARAM = Renderable400("Weights (between 0 and 100) are required if you are randomizing with weights. Please go back and submit weights for all tracks.")
INVALID_URL_PARAM = Renderable400("One of your URL inputs is invalid.")
PARAM_LENGTH_EXCEEDS_LIMIT = Renderable400("There are length limitations. At least one of your inputs is too long.")

COPIES_EXCEEDS_LIMIT = Renderable400("There exists too many copies of the experiment you are trying to copy. Please delete some before copying.")
UNIQUE_NAME_ERROR = Renderable400("Another intervention point with this name was found in the database. Names must be unique. Ensure you are using a different name and please try again.")
CSV_ERROR = Renderable500("There was a problem preparing the CSV file for download.")


def DATABASE_ERROR(error_message):
    return Renderable400(ADMIN_VISIBLE_ERROR)

def missing_param_error(param_name):
    return Renderable400(ADMIN_VISIBLE_ERROR)
