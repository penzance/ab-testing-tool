from error_middleware.exceptions import (Renderable500, Renderable400,
    Renderable403, Renderable404)

NO_SDK_RESPONSE = Renderable500("Canvas SKD returned an error")

MISSING_LTI_LAUNCH = Renderable400("LTI_LAUNCH not in session")
MISSING_LTI_PARAM = Renderable400("Missing LTI parameter in session")

BAD_STAGE_ID = Renderable400("Invalid stage id")

DELETING_INSTALLED_STAGE = Renderable400("Deleting an installed Intervention Point is not allowed")

UNAUTHORIZED_ACCESS = Renderable403("You do not have access to this course.")

MISSING_RETURN_TYPES_PARAM = Renderable400("Invalid ext_content_return_types")

MISSING_RETURN_URL = Renderable400("No ext_content_return_url")

COURSE_TRACKS_ALREADY_FINALIZED = Renderable400("You can't change tracks after their finalized")
COURSE_TRACKS_NOT_FINALIZED = Renderable400("Course tracks are not finalized")
NO_URL_FOR_TRACK = Renderable404("No course content. Ask your course instructors to put something here.")
NO_TRACKS_FOR_COURSE = Renderable404("No tracks have been configured for this course.")

def missing_param_error(param_name):
    return Renderable400("Missing POST parameter %s" % param_name)
