from pydantic import BaseModel, Field

class FibonacciRequest(BaseModel):
    """
    Request model for Fibonacci endpoint.

    Attributes:
        n: The Fibonacci sequence index to compute (1-based).
            Must be between 1 and 1000 inclusive.
    """
    n: int = Field(..., example=5, ge=1, le=1000, description="Index in the Fibonacci sequence (1 to 1000)")