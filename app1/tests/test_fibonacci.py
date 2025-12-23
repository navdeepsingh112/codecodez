import pytest
from app.fibonacci import calculate_fibonacci_sequence

def test_calculate_fibonacci_sequence():
    """
    Test cases for Fibonacci sequence calculation.
    Verifies base cases, standard sequence, large input performance, and error handling.
    """
    # Test n=0: should return single element [0]
    assert calculate_fibonacci_sequence(0) == [0]
    
    # Test n=1: should return [0, 1]
    assert calculate_fibonacci_sequence(1) == [0, 1]
    
    # Test n=5: verify full sequence [0, 1, 1, 2, 3, 5]
    assert calculate_fibonacci_sequence(5) == [0, 1, 1, 2, 3, 5]
    
    # Test n=100: verify sequence length and recurrence relation
    result = calculate_fibonacci_sequence(100)
    assert len(result) == 101
    for i in range(2, 101):
        assert result[i] == result[i-1] + result[i-2]
    
    # Test negative input: should raise ValueError
    with pytest.raises(ValueError):
        calculate_fibonacci_sequence(-1)