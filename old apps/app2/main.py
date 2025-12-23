from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def read_root():
    """
    Root endpoint that returns the application status.

    Returns:
        dict: A dictionary with the status key set to 'running'.
    """
    return {"status": "running"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handles HTTPException instances by returning a JSON response with the appropriate status code and message.

    Args:
        request (Request): The incoming request.
        exc (HTTPException): The exception instance.

    Returns:
        JSONResponse: A JSON response with the status code and message.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handles unhandled exceptions by returning a generic 500 error response.

    Args:
        request (Request): The incoming request.
        exc (Exception): The exception instance.

    Returns:
        JSONResponse: A JSON response indicating an internal server error.
    """
    return JSONResponse(status_code=500, content={"message": "Internal server error"})

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title='Fibonacci API',
    description='Calculate Fibonacci numbers'
)

class FibonacciRequest(BaseModel):
    n: int = Field(..., example=5)

class FibonacciResponse(BaseModel):
    result: int = Field(..., example=8)

def configure_metadata() -> None:
    app.openapi_tags = [
        {
            'name': 'fibonacci',
            'description': 'Endpoints to compute Fibonacci numbers.'
        }
    ]
    app.swagger_ui_parameters = {
        'defaultModelsExpandDepth': -1,
        'defaultModelExpandDepth': 2,
        'displayRequestDuration': True,
        'docExpansion': 'none',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
    }
    app.redoc_ui_parameters = {
        'hideDownloadButton': False,
        'hideHostname': True,
        'expandResponses': 'default',
        'showExtensions': True,
        'pathInMiddle': True,
    }

configure_metadata()