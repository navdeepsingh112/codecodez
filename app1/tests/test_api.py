import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.config import MAX_N

def test_fibonacci_endpoint():
    """
    Test the Fibonacci API endpoint for various scenarios:
    1. Valid input returns 200 and correct sequence
    2. n > MAX_N returns 400
    3. Negative n returns 400
    4. Non-integer input returns 422
    5. Verify response JSON structure
    6. Test CORS headers
    """
    app = create_app()
    client = TestClient(app)
    
    # Test valid input
    valid_n = 5
    response = client.get(f"/fibonacci/{valid_n}")
    assert response.status_code == 200
    assert response.json() == {"sequence": [0, 1, 1, 2, 3]}
    
    # Test n exceeding MAX_N
    large_n = MAX_N + 1
    response = client.get(f"/fibonacci/{large_n}")
    assert response.status_code == 400
    assert "exceeds maximum allowed value" in response.json()["detail"]
    
    # Test negative input
    negative_n = -5
    response = client.get(f"/fibonacci/{negative_n}")
    assert response.status_code == 400
    assert "must be non-negative" in response.json()["detail"]
    
    # Test non-integer input
    non_int = "abc"
    response = client.get(f"/fibonacci/{non_int}")
    assert response.status_code == 422
    assert "value is not a valid integer" in response.json()["detail"]
    
    # Test response structure for valid input
    response = client.get("/fibonacci/1")
    assert response.status_code == 200
    data = response.json()
    assert "sequence" in data
    assert isinstance(data["sequence"], list)
    assert all(isinstance(num, int) for num in data["sequence"])
    
    # Test CORS headers
    origin = "http://testorigin.com"
    headers = {"Origin": origin}
    response = client.get("/fibonacci/3", headers=headers)
    assert response.headers["access-control-allow-origin"] == origin