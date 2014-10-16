from error_middleware.exceptions import (Renderable500, Renderable400,
    Renderable403, Renderable404)

NO_SDK_RESPONSE = Renderable500("Canvas SDK returned an error")

MISSING_LTI_LAUNCH = Renderable400("LTI_LAUNCH not in session")
MISSING_LTI_PARAM = Renderable400("Missing LTI parameter in session")

BAD_STAGE_ID = Renderable400("Invalid intervention_point id")

DELETING_INSTALLED_STAGE = Renderable400("Deleting an installed Intervention Point is not allowed")

UNAUTHORIZED_ACCESS = Renderable403("You do not have access to this course.")

MISSING_RETURN_TYPES_PARAM = Renderable400("Invalid ext_content_return_types")

MISSING_RETURN_URL = Renderable400("No ext_content_return_url")

COURSE_TRACKS_ALREADY_FINALIZED = Renderable400("You can't change tracks after their finalizing")
COURSE_TRACKS_NOT_FINALIZED = Renderable400("Course tracks are not finalized")
NO_URL_FOR_TRACK = Renderable404("No course content. If you are a student, notify your course instructors regarding this page before returning here.")
NO_TRACKS_FOR_COURSE = Renderable404("No tracks have been configured for this course. If you are a student, notify your course instructors regarding this page before returning here.")

CSV_UPLOAD_NEEDED = Renderable404("New CSV upload needed. If you are a student, notify your course instructors regarding this page before returning here.")
TRACK_WEIGHTS_NOT_SET = Renderable404("Missing track configuration. If you are a student, notify your course instructors regarding this page before returning here.")
INPUT_NOT_ALLOWED = Renderable404("Input does not follow requirements")

def missing_param_error(param_name):
    return Renderable400("Missing POST parameter %s" % param_name)
