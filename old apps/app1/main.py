from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict

app = FastAPI(
    title="Basic FastAPI App",
    description="A simple FastAPI application setup",
    version="0.1.0",
)

@app.get("/")
def read_root() -> Dict[str, str]:
    """Return a welcome message."""
    return {"message": "Hello, World!"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions and return a JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions and return a 500 JSON response."""
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)