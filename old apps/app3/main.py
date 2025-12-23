

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.v1.fibonacci import router

class FibonacciError(Exception):
    def __init__(self, message: str):
        self.message = message

app = FastAPI(title="Fibonacci API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["fibonacci"])

@app.exception_handler(FibonacciError)
async def fibonacci_exception_handler(request: Request, exc: FibonacciError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message},
    )

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Hello, World!"}