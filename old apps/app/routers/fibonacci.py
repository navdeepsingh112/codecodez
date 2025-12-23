from fastapi import APIRouter, Depends, HTTPException
from ..schemas import FibonacciRequest, FibonacciResponse
from ..utils.calculations import compute_fibonacci
from ..dependencies import get_fib_cache

router = APIRouter()

@router.post('/fibonacci', response_model=FibonacciResponse)
def fib_endpoint(request: FibonacciRequest, cache: dict = Depends(get_fib_cache)):
    """
    Calculate the Fibonacci sequence value for a given index.
    
    Args:
        request: FibonacciRequest model containing the index 'n'
        cache: In-memory cache dictionary for storing computed results
    
    Returns:
        FibonacciResponse containing the computed result
    
    Raises:
        HTTPException: For invalid input or computation errors
    """
    n = request.n
    
    if n > 1000:
        raise HTTPException(
            status_code=400,
            detail="Input value exceeds maximum allowed limit of 1000"
        )
    
    if n in cache:
        return FibonacciResponse(result=cache[n])
    
    try:
        result = compute_fibonacci(n)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during computation: {str(e)}"
        )
    
    cache[n] = result
    return FibonacciResponse(result=result)