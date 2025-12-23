from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .fibonacci import calculate_fibonacci_sequence
from .schemas import FibonacciResponse
from .config import MAX_N, DEFAULT_MAX_N_MESSAGE
from .errors import http_error_handler

def create_app() -> FastAPI:
    """
    Initialize and configure the FastAPI application.
    
    This function:
    1. Creates a FastAPI instance
    2. Sets up CORS middleware
    3. Registers custom error handlers
    4. Defines application routes
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI()
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register error handlers
    app.add_exception_handler(HTTPException, http_error_handler)
    
    @app.get("/fibonacci/{n}", response_model=FibonacciResponse)
    async def get_fibonacci(n: int) -> FibonacciResponse:
        """
        Calculate Fibonacci sequence up to n elements.
        
        Args:
            n: Number of Fibonacci sequence elements to calculate (0-indexed)
        
        Returns:
            FibonacciResponse: Object containing the sequence and parameters
            
        Raises:
            HTTPException: 400 if n is outside allowed range [0, MAX_N]
        """
        if n < 0 or n > MAX_N:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=DEFAULT_MAX_N_MESSAGE.format(max_n=MAX_N)
            )
        
        sequence = calculate_fibonacci_sequence(n)
        return FibonacciResponse(sequence=sequence, parameters={"n": n})
    
    return app