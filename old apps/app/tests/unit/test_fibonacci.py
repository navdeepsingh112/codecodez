import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..utils.calculations import calculate_fibonacci

def test_calculate_fibonacci():
    """
    Test the calculate_fibonacci function with various inputs.
    Includes valid, edge, and invalid cases along with cache verification.
    """
    # Test valid and edge cases
    assert calculate_fibonacci(0) == 0
    assert calculate_fibonacci(1) == 1
    assert calculate_fibonacci(5) == 5
    assert calculate_fibonacci(10) == 55
    
    # Test large number
    result = calculate_fibonacci(1000)
    assert isinstance(result, int)
    assert len(str(result)) == 209  # fib(1000) has 209 digits
    
    # Test invalid inputs
    with pytest.raises(ValueError):
        calculate_fibonacci(-5)
    with pytest.raises(TypeError):
        calculate_fibonacci("invalid")
    with pytest.raises(TypeError):
        calculate_fibonacci(5.5)
    
    # Test cache functionality
    if hasattr(calculate_fibonacci, 'cache_clear'):
        calculate_fibonacci.cache_clear()
        calculate_fibonacci(20)  # First call - should cache
        calculate_fibonacci(20)  # Second call - should use cache
        cache_info = calculate_fibonacci.cache_info()
        assert cache_info.hits == 1
        assert cache_info.misses == 1
    else:
        pytest.fail("Cache not implemented for calculate_fibonacci")

def test_fib_endpoint():
    """
    Test the Fibonacci API endpoint using TestClient.
    Covers response validation, status codes, and error handling.
    """
    client = TestClient(app)
    
    # Test valid inputs
    test_cases = [(0, 0), (1, 1), (5, 5), (10, 55)]
    for n, expected in test_cases:
        response = client.post("/fibonacci", json={"n": n})
        assert response.status_code == 200
        assert response.json() == {"result": expected}
    
    # Test large number
    response = client.post("/fibonacci", json={"n": 1000})
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert isinstance(data["result"], int)
    assert len(str(data["result"])) == 209
    
    # Test invalid inputs
    invalid_cases = [-5, "invalid", 5.5]
    for n in invalid_cases:
        response = client.post("/fibonacci", json={"n": n})
        assert response.status_code == 422
    
    # Test unsupported HTTP methods
    methods = ["get", "put", "delete", "patch", "head", "options"]
    for method in methods:
        response = getattr(client, method)("/fibonacci")
        assert response.status_code == 405