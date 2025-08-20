from fastapi.testclient import TestClient
from http import HTTPStatus
from typing import Any, Dict, List
import pytest

# Assuming the FastAPI app is defined in 'api' module
from api import app

client = TestClient(app)

def test_get_fibonacci_number_valid() -> None:
    """Test valid request for nth Fibonacci number."""
    response: Any = client.get("/fibonacci/number", params={"n": 5})
    assert response.status_code == HTTPStatus.OK
    data: Dict[str, int] = response.json()
    assert data == {"n": 5, "value": 5}

def test_get_fibonacci_number_zero() -> None:
    """Test request for n=0."""
    response: Any = client.get("/fibonacci/number", params={"n": 0})
    assert response.status_code == HTTPStatus.OK
    data: Dict[str, int] = response.json()
    assert data == {"n": 0, "value": 0}

def test_get_fibonacci_number_one() -> None:
    """Test request for n=1."""
    response: Any = client.get("/fibonacci/number", params={"n": 1})
    assert response.status_code == HTTPStatus.OK
    data: Dict[str, int] = response.json()
    assert data == {"n": 1, "value": 1}

def test_get_fibonacci_number_negative() -> None:
    """Test invalid request with negative n."""
    response: Any = client.get("/fibonacci/number", params={"n": -1})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data: Dict[str, str] = response.json()
    assert data == {"detail": "n must be a non-negative integer"}

def test_get_fibonacci_number_non_integer() -> None:
    """Test invalid request with non-integer n."""
    response: Any = client.get("/fibonacci/number", params={"n": "a"})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data: Dict[str, List[Dict[str, str]]] = response.json()
    assert data["detail"][0]["msg"] == "value is not a valid integer"

def test_get_fibonacci_sequence_valid() -> None:
    """Test valid sequence request with limit=5."""
    response: Any = client.get("/fibonacci/sequence", params={"limit": 5})
    assert response.status_code == HTTPStatus.OK
    data: List[int] = response.json()
    assert data == [0, 1, 1, 2, 3]

def test_get_fibonacci_sequence_limit_zero() -> None:
    """Test sequence request with limit=0."""
    response: Any = client.get("/fibonacci/sequence", params={"limit": 0})
    assert response.status_code == HTTPStatus.OK
    data: List[int] = response.json()
    assert data == []

def test_get_fibonacci_sequence_limit_one() -> None:
    """Test sequence request with limit=1."""
    response: Any = client.get("/fibonacci/sequence", params={"limit": 1})
    assert response.status_code == HTTPStatus.OK
    data: List[int] = response.json()
    assert data == [0, 1]

def test_get_fibonacci_sequence_negative_limit() -> None:
    """Test invalid sequence request with negative limit."""
    response: Any = client.get("/fibonacci/sequence", params={"limit": -1})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data: Dict[str, str] = response.json()
    assert data == {"detail": "limit must be a non-negative integer"}

def test_get_fibonacci_sequence_non_integer_limit() -> None:
    """Test invalid sequence request with non-integer limit."""
    response: Any = client.get("/fibonacci/sequence", params={"limit": "a"})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data: Dict[str, List[Dict[str, str]]] = response.json()
    assert data["detail"][0]["msg"] == "value is not a valid integer"

def test_get_fibonacci_sequence_max_limit() -> None:
    """Test sequence request with maximum limit (e.g., 1000)."""
    response: Any = client.get("/fibonacci/sequence", params={"limit": 1000})
    assert response.status_code == HTTPStatus.OK
    data: List[int] = response.json()
    assert len(data) == 1000
    assert data[:5] == [0, 1, 1, 2, 3]