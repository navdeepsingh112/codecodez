def validate_fibonacci_input(n: int) -> None:
    """Validate that n is a non-negative integer and within acceptable range.

    Args:
        n (int): The input to validate.

    Raises:
        ValueError: If n is not an integer or is negative.
    """
    if not isinstance(n, int):
        raise ValueError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")