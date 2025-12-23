def calculate_fibonacci(n: int) -> list[int]:
    """
    Compute the Fibonacci sequence iteratively with O(n) complexity.

    Args:
        n: The number of Fibonacci numbers to generate (non-negative integer).

    Returns:
        A list containing the first n Fibonacci numbers.

    Raises:
        ValueError: If n is negative.

    Examples:
        >>> calculate_fibonacci(5)
        [0, 1, 1, 2, 3]
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if n == 0:
        return []
    if n == 1:
        return [0]
    
    sequence = [0, 1]
    for i in range(2, n):
        next_value = sequence[-1] + sequence[-2]
        sequence.append(next_value)
    
    return sequence