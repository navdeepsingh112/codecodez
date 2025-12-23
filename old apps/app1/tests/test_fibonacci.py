from typing import List, Dict, Union

def generate_fibonacci_tests() -> List[Dict[str, Union[int, str]]]:
    """
    Generate test cases for the Fibonacci function.

    Returns:
        List of dictionaries with 'input' and 'expected' keys.
        Valid inputs (n >= 1) return the nth Fibonacci number.
        Invalid inputs (n <= 0) return an error message.
    """
    valid = [
        {'input': 1, 'expected': 0},
        {'input': 2, 'expected': 1},
        {'input': 3, 'expected': 1},
        {'input': 4, 'expected': 2},
        {'input': 5, 'expected': 3},
        {'input': 6, 'expected': 5},
        {'input': 7, 'expected': 8},
        {'input': 10, 'expected': 34},
        {'input': 1000, 'expected': 43466557686937456435688527675040674983795833071362631418149104505097975435621344},
    ]
    invalid = [
        {'input': 0, 'expected': 'Error'},
        {'input': -5, 'expected': 'Error'},
    ]
    return valid + invalid

def generate_api_tests() -> List[Dict[str, str]]:
    """
    Generate test cases for API endpoints.

    Returns:
        List of dictionaries with 'url' and 'expected_status' keys.
    """
    return [
        {'url': '/fibonacci/5', 'expected_status': '200'},
        {'url': '/fibonacci/0', 'expected_status': '400'},
        {'url': '/fibonacci/-5', 'expected_status': '400'},
        {'url': '/fibonacci/1000', 'expected_status': '200'},
    ]