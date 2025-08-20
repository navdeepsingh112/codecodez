import os

class Settings:
    MAX_FIBONACCI_N: int
    MAX_SEQUENCE_LIMIT: int

    def __init__(self) -> None:
        try:
            val = os.getenv('MAX_FIBONACCI_N', '1000').strip()
            self.MAX_FIBONACCI_N = int(val)
        except ValueError:
            self.MAX_FIBONACCI_N = 1000
        try:
            val = os.getenv('MAX_SEQUENCE_LIMIT', '1000').strip()
            self.MAX_SEQUENCE_LIMIT = int(val)
        except ValueError:
            self.MAX_SEQUENCE_LIMIT = 1000

settings = Settings()