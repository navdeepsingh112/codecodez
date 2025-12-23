from fastapi import APIRouter, Path
from ..services.fibonacci import calculate_fibonacci

router = APIRouter()

@router.get('/fib')
def get_fibonacci_sequence(n: int = Path(..., gt=0, le=1000)) -> dict:
    """
    Generate Fibonacci sequence up to n terms.
    
    Args:
        n: Number of terms to generate (1-1000 inclusive)
    
    Returns:
        Dictionary containing the Fibonacci sequence as a list under 'sequence' key
    
    Raises:
        HTTPException: If input validation fails (handled by FastAPI Path)
    """
    sequence = calculate_fibonacci(n)
    return {'sequence': sequence}