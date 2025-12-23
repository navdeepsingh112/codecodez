from pydantic import BaseModel
from typing import List


class FibonacciResponse(BaseModel):
    """
    Response model for Fibonacci sequence API endpoint.

    Attributes:
        sequence: List of integers representing the Fibonacci sequence.
    """
    sequence: List[int]

    class Config:
        schema_extra = {
            "example": {
                "sequence": [0, 1, 1, 2, 3, 5, 8]
            }
        }