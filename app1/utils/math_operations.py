def calculate_fibonacci(n: int) -> int:
    """Compute the nth Fibonacci number using an iterative approach.

    Args:
        n (int): The index of the Fibonacci number to compute (0-based).

    Returns:
        int: The nth Fibonacci number.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b