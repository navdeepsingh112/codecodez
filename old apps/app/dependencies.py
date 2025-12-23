from cachetools import LRUCache
from typing import Any

def get_fib_cache() -> LRUCache:
    """
    Dependency function that provides a shared LRU cache for Fibonacci results.
    
    Creates and returns a singleton LRUCache instance with maxsize=128. The same cache 
    instance is reused across all dependency calls after initial creation.
    
    Returns:
        LRUCache: Singleton instance of LRU cache for storing Fibonacci sequence results
    """
    if not hasattr(get_fib_cache, "_cache"):
        setattr(get_fib_cache, "_cache", LRUCache(maxsize=128))
    return get_fib_cache._cache