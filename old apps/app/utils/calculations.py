from typing import List

def calculate_fibonacci(n: int) -> List[int]:
    """
    Generate the first n Fibonacci numbers iteratively.

    The Fibonacci sequence starts with 0 and 1. Each subsequent number is the sum
    of the two preceding ones. Returns an empty list for n=0.

    Args:
        n: The number of Fibonacci numbers to generate.

    Returns:
        A list containing the first n Fibonacci numbers.

    Examples:
        >>> calculate_fibonacci(0)
        []
        >>> calculate_fibonacci(1)
        [0]
        >>> calculate_fibonacci(5)
        [0, 1, 1, 2, 3]
    """
    if n <= 0:
        return []
    
    sequence = [0, 1]
    if n <= 2:
        return sequence[:n]
    
    for _ in range(2, n):
        next_num = sequence[-1] + sequence[-2]
        sequence.append(next_num)
    
    return sequence