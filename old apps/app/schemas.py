from pydantic import BaseModel, Field
from typing import List

class FibonacciRequest(BaseModel):
    """
    Request model for Fibonacci sequence generation.
    
    Attributes:
        n: The number of Fibonacci numbers to generate. Must be between 0 and 1000 inclusive.
    """
    n: int = Field(ge=0, le=1000, description="Number of Fibonacci sequence elements to generate (0-1000)")

class FibonacciResponse(BaseModel):
    """
    Response model containing Fibonacci sequence.
    
    Attributes:
        sequence: List of Fibonacci numbers starting from F(0).
    """
    sequence: List[int] = Field(description="Generated Fibonacci sequence as list of integers")