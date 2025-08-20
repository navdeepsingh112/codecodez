class InvalidFibonacciInputError(Exception):
    """Custom exception for invalid Fibonacci input."""
    pass

def calculate_fibonacci_number(n: int) -> int:
    if not isinstance(n, int) or n < 0:
        raise InvalidFibonacciInputError("n must be a non-negative integer.")
    if n == 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def calculate_fibonacci_sequence(limit: int) -> list:
    if not isinstance(limit, int) or limit < 0:
        raise InvalidFibonacciInputError("limit must be a non-negative integer.")
    sequence = []
    a, b = 0, 1
    while a <= limit:
        sequence.append(a)
        a, b = b, a + b
    return sequence