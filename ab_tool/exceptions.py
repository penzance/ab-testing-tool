from error_middleware.exceptions import (Renderable500, Renderable400,
    Renderable403, Renderable404)

import logging
import traceback

logger = logging.getLogger(__name__)

NO_SDK_RESPONSE = Renderable500("Canvas SDK returned an error")

MISSING_LTI_LAUNCH = Renderable400("LTI_LAUNCH not in session")
MISSING_LTI_PARAM = Renderable400("Missing LTI parameter in session")

BAD_STAGE_ID = Renderable400("Invalid intervention_point id")

DELETING_INSTALLED_STAGE = Renderable400("Deleting an installed Intervention Point is not allowed")

UNAUTHORIZED_ACCESS = Renderable403("You do not have access to this course.")

MISSING_RETURN_TYPES_PARAM = Renderable400("Invalid ext_content_return_types")

MISSING_RETURN_URL = Renderable400("No ext_content_return_url")

EXPERIMENT_TRACKS_ALREADY_FINALIZED = Renderable400("You can't edit or delete the experiment after it has been started.")
INTERVENTION_POINTS_ARE_INSTALLED = Renderable400("You can't edit or delete the experiment if there are intervention points installed for the experiment.")
EXPERIMENT_TRACKS_NOT_FINALIZED = Renderable400("Experiment tracks are not finalized")
NO_URL_FOR_TRACK = Renderable404("No course content. Ask your course instructors to put something here.")
NO_TRACKS_FOR_EXPERIMENT = Renderable404("No tracks have been configured for this experiment.")

CSV_UPLOAD_NEEDED = Renderable404("New CSV upload needed. If you are a student, notify your course instructors regarding this page before returning here.")
TRACK_WEIGHTS_NOT_SET = Renderable404("Missing track configuration. If you are a student, notify your course instructors regarding this page before returning here.")
INPUT_NOT_ALLOWED = Renderable404("Input does not follow requirements")

MISSING_NAME_PARAM = Renderable400("Names are required. Please go back and submit a name for all experiments, tracks, and intervention points.")
INCORRECT_WEIGHTING_PARAM = Renderable400("Weights (between 0 and 100) are required if you are randomizing with weights. Please go back and submit weights for all tracks.")
INVALID_URL_PARAM = Renderable400("One of your URL inputs is invalid.")

def DATABASE_ERROR(error_message):
    return Renderable400("%s" % error_message)

CSV_ERROR = Renderable500("There was a problem preparing the CSV file for download")

def missing_param_error(param_name):
    return Renderable400("Missing POST parameter %s" % param_name)
