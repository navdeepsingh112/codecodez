from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

async def handle_validation_errors(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Custom error handler for validation errors. Formats the errors into a user-friendly JSON response.

    Args:
        request (Request): The incoming request.
        exc (RequestValidationError): The validation error exception.

    Returns:
        JSONResponse: A JSON response containing the error messages.
    """
    errors = []
    for error in exc.errors():
        loc = error.get('loc', [])
        error_type = error.get('type')
        ctx = error.get('ctx', {})
        field = loc[-1] if loc else 'unknown field'
        msg = error.get('msg', 'An unknown error occurred')

        if loc == ['path', 'number']:
            if error_type == 'type_error.integer':
                errors.append({
                    'field': 'number',
                    'message': f"The number provided in the URL must be an integer. You provided '{ctx.get('value', '')}'."
                })
            elif error_type == 'value_error.number.not_ge_zero':
                errors.append({
                    'field': 'number',
                    'message': f"The number must be non-negative. You provided {ctx.get('value', '')}."
                })
            elif error_type == 'value_error.number.too_large':
                limit = ctx.get('limit_value', 'unknown limit')
                value = ctx.get('value', 'unknown value')
                errors.append({
                    'field': 'number',
                    'message': f"The number cannot exceed {limit}. You provided {value}."
                })
            else:
                errors.append({
                    'field': 'number',
                    'message': f"Invalid value: {msg}"
                })
        else:
            errors.append({
                'field': field,
                'message': f"Invalid value: {msg}"
            })

    return JSONResponse(status_code=400, content={'errors': errors})