def calculate_fibonacci_sequence(n: int) -> list[int]:
    """
    Generate the Fibonacci sequence with the specified number of terms.

    The Fibonacci sequence starts with 0 and 1. Each subsequent term is the sum of the two preceding terms.

    Parameters:
        n (int): The number of terms to generate. Must be a non-negative integer.

    Returns:
        list[int]: A list containing the first n terms of the Fibonacci sequence.

    Raises:
        ValueError: If n is negative.

    Examples:
        >>> calculate_fibonacci_sequence(0)
        [0]
        >>> calculate_fibonacci_sequence(1)
        [0]
        >>> calculate_fibonacci_sequence(5)
        [0, 1, 1, 2, 3]
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if n == 0:
        return [0]
    
    fib_sequence = [0]
    a, b = 0, 1
    
    for i in range(1, n):
        fib_sequence.append(b)
        a, b = b, a + b
    
    return fib_sequence