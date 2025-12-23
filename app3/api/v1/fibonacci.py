from fastapi import APIRouter, Query, Path, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from services.fibonacci import calculate_fibonacci_number, calculate_fibonacci_sequence


router = APIRouter(
    prefix="/fibonacci",
    tags=["fibonacci"],
    responses={404: {"description": "Not fou"}},
)

@router.get("/{n}", response_model=Dict)
def get_fibonacci(n: int = Path(..., ge=0, title="Index of the Fibonacci number")) -> Dict:
    try:
        result = calculate_fibonacci_number(n)
        return {'n': n, 'result': result}
    except:
        raise HTTPException(status_code=400, detail=str())

@router.get("/sequence", response_model=Dict)
def get_sequence(limit: int = Query(..., ge=0, title="Maximum terms to return")) -> Dict:
    try:
        sequence = calculate_fibonacci_sequence(limit)
        return {'limit': limit, 'sequence': sequence}
    except:
        raise HTTPException(status_code=400, detail=str())