from error_middleware.middleware import RenderableError

NO_SDK_RESPONSE = RenderableError("Canvas SKD returned an error")

MISSING_LTI_LAUNCH = RenderableError("LTI_LAUNCH not in session")
MISSING_LTI_PARAM = RenderableError("Missing LTI parameter in session")

BAD_STAGE_ID = RenderableError("Invalid stage id")

MISSING_STAGE = RenderableError("No stage found matching database query")
MISSING_TRACK = RenderableError("No track found matching database query")

DELETING_INSTALLED_STAGE = RenderableError("Deleting an installed Stage is not allowed")

UNAUTHORIZED_ACCESS = RenderableError("You do not have access to this course.")

MISSING_RETURN_TYPES_PARAM = RenderableError("Invalid ext_content_return_types")

MISSING_RETURN_URL = RenderableError("No ext_content_return_url")

COURSE_TRACKS_ALREADY_FINALIZED = RenderableError("You can't change tracks after their finalized")
COURSE_TRACKS_NOT_FINALIZED = RenderableError("Course tracks are not finalized")
NO_URL_FOR_TRACK = RenderableError("No course content. Ask your course instructors to put something here.")
NO_TRACKS_FOR_COURSE = RenderableError("No tracks have been configured for this course.")

def missing_param_error(param_name):
    return RenderableError("Missing POST parameter %s" % param_name)