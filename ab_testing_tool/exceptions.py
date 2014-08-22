class InvalidResponseError(Exception):
    """ TODO: Move this to canvas_sdk_python """
    pass

NO_SDK_RESPONSE = InvalidResponseError("Canvas SKD returned an error")
INVALID_SDK_RESPONSE = InvalidResponseError("Response from canvas SDK was invalid")

MISSING_LTI_LAUNCH = Exception("LTI_LAUNCH not in session")
MISSING_LTI_PARAM = Exception("Missing LTI parameter in session")

BAD_STAGE_ID = Exception("Invalid stage id")

MISSING_STAGE = Exception("No stage found matching database query")
MISSING_TRACK = Exception("No track found matching database query")

MULTIPLE_OBJECTS = Exception("Multiple objects returned by database query.")

DELETING_INSTALLED_STAGE = Exception("Deleting an installed Stage is not allowed")
