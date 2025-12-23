import re
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom exception handler for HTTPException.
    
    Returns a JSON response with standardized error format. Handles special case
    where error detail contains negative numbers by replacing the message.
    
    Args:
        request: The incoming request object
        exc: The raised HTTPException instance
        
    Returns:
        JSONResponse: Formatted error response containing:
            - error: HTTP status code
            - message: Error detail message (customized for negative numbers)
    """
    detail = exc.detail
    message = str(detail)
    
    # Check for negative numbers in error detail
    if isinstance(detail, (int, float)) and detail < 0:
        message = "Negative numbers are not allowed"
    elif isinstance(detail, str) and re.search(r'-\d+', detail):
        message = "Negative numbers are not allowed"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.status_code,
            "message": message
        }
    )