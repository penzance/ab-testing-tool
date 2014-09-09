class InvalidResponseError(Exception):
    """ TODO: Move this to canvas_sdk_python """
    pass

NO_SDK_RESPONSE = InvalidResponseError("Canvas SKD returned an error")

MISSING_LTI_LAUNCH = Exception("LTI_LAUNCH not in session")
MISSING_LTI_PARAM = Exception("Missing LTI parameter in session")

BAD_STAGE_ID = Exception("Invalid stage id")

MISSING_STAGE = Exception("No stage found matching database query")
MISSING_TRACK = Exception("No track found matching database query")

DELETING_INSTALLED_STAGE = Exception("Deleting an installed Stage is not allowed")

UNAUTHORIZED_ACCESS = Exception("You do not have access to this course.")

MISSING_RETURN_TYPES_PARAM = Exception("Invalid ext_content_return_types")

MISSING_RETURN_URL = Exception("No ext_content_return_url")

COURSE_TRACKS_ALREADY_FINALIZED = Exception("You can't change tracks after their finalized")
COURSE_TRACKS_NOT_FINALIZED = Exception("Course tracks are not finalized")
NO_URL_FOR_TRACK = Exception("No course content. Ask your course instructors to put something here.")
NO_TRACKS_FOR_COURSE = Exception("No tracks have been configured for this course.")
