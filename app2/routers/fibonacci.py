from fastapi import APIRouter, HTTPException
from services.fibonacci import calculate_fibonacci

router = APIRouter()

@router.get("/fibonacci/{n}", tags=["Fibonacci"], response_model=dict)
async def get_fibonacci(n: int):
    """
    Calculate the nth Fibonacci number.

    Parameters:
    n (int): The position in the Fibonacci sequence (0-based).

    Returns:
    dict: A dictionary with the input n and the calculated Fibonacci value.
    """
    if n < 0 or n > 1000:
        raise HTTPException(status_code=400, detail="n must be between 0 and 1000")
    fib_value = calculate_fibonacci(n)
    return {"n": n, "fibonacci_value": fib_value}

from fastapi import HTTPException

def validate_fibonacci_input(n: int) -> int:
    """
    Validate the input for the Fibonacci function.

    Args:
        n (int): The index in the Fibonacci sequence.

    Returns:
        int: The validated index.

    Raises:
        HTTPException: If n is not an integer or is out of range (0-1000).
    """
    if not isinstance(n, int):
        raise HTTPException(status_code=400, detail="n must be an integer")
    if n < 0 or n > 1000:
        raise HTTPException(status_code=400, detail="n must be between 0 and 1000")
    return n