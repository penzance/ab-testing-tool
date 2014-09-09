from error_middleware.middleware import UserDisplayError

NO_SDK_RESPONSE = UserDisplayError("Canvas SKD returned an error")

MISSING_LTI_LAUNCH = UserDisplayError("LTI_LAUNCH not in session")
MISSING_LTI_PARAM = UserDisplayError("Missing LTI parameter in session")

BAD_STAGE_ID = UserDisplayError("Invalid stage id")

MISSING_STAGE = UserDisplayError("No stage found matching database query")
MISSING_TRACK = UserDisplayError("No track found matching database query")

DELETING_INSTALLED_STAGE = UserDisplayError("Deleting an installed Stage is not allowed")

UNAUTHORIZED_ACCESS = UserDisplayError("You do not have access to this course.")

MISSING_RETURN_TYPES_PARAM = UserDisplayError("Invalid ext_content_return_types")

MISSING_RETURN_URL = UserDisplayError("No ext_content_return_url")

COURSE_TRACKS_ALREADY_FINALIZED = UserDisplayError("You can't change tracks after their finalized")
COURSE_TRACKS_NOT_FINALIZED = UserDisplayError("Course tracks are not finalized")
NO_URL_FOR_TRACK = UserDisplayError("No course content. Ask your course instructors to put something here.")
NO_TRACKS_FOR_COURSE = UserDisplayError("No tracks have been configured for this course.")
