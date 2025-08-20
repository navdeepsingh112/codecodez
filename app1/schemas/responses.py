def error_response() -> dict:
    """
    Returns a standardized error response for invalid requests.

    Returns:
        dict: A dictionary containing the error code and message.
    """
    return {
        "error": "invalid_request",
        "message": "The request is invalid. Please check your input and try again."
    }