def calculate_fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number using an iterative approach.

    Parameters:
    n (int): The position in the Fibonacci sequence (0-based index).

    Returns:
    int: The nth Fibonacci number.

    Raises:
    ValueError: If n is not a non-negative integer.

    Examples:
    >>> calculate_fibonacci(0)
    0
    >>> calculate_fibonacci(1)
    1
    >>> calculate_fibonacci(10)
    55
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b