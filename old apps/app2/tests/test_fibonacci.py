from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fibonacci_zero():
    """Test Fibonacci with n=0."""
    response = client.get('/fibonacci/0')
    assert response.status_code == 200
    assert response.json() == {'n': 0, 'fibonacci_value': 0}

def test_fibonacci_one():
    """Test Fibonacci with n=1."""
    response = client.get('/fibonacci/1')
    assert response.status_code == 200
    assert response.json() == {'n': 1, 'fibonacci_value': 1}

def test_fibonacci_ten():
    """Test Fibonacci with n=10."""
    response = client.get('/fibonacci/10')
    assert response.status_code == 200
    assert response.json() == {'n': 10, 'fibonacci_value': 55}

def test_fibonacci_negative():
    """Test Fibonacci with negative n."""
    response = client.get('/fibonacci/-5')
    assert response.status_code == 400
    assert 'detail' in response.json()

def test_fibonacci_non_integer():
    """Test Fibonacci with non-integer n."""
    response = client.get('/fibonacci/abc')
    assert response.status_code == 422
    assert 'detail' in response.json()