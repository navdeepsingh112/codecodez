def get_fibonacci_number(n: int) -> dict:
    """Compute the nth Fibonacci number.

    Args:
        n (int): The position in the Fibonacci sequence (0-based).

    Returns:
        dict: A dictionary with either 'result' or 'error' key.
    """
    if n < 0:
        return {'error': 'n must be a non-negative integer'}

    if n == 0:
        return {'result': 0}
    elif n == 1:
        return {'result': 1}

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b

    return {'result': b}