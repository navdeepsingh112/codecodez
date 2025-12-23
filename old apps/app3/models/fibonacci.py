from pydantic import BaseModel, conint
from config import MAX_FIBONACCI_N, MAX_SEQUENCE_LIMIT

class FibonacciNumberRequest(BaseModel):
    """Request model for getting a Fibonacci number by index."""
    n: conint(ge=0, le=MAX_FIBONACCI_N)

class FibonacciSequenceRequest(BaseModel):
    """Request model for getting a Fibonacci sequence up to a limit."""
    limit: conint(ge=0, le=MAX_SEQUENCE_LIMIT)