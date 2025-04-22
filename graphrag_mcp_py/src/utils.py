"""
Utility functions for GraphRAG MCP server.
"""

import logging
import time
from functools import lru_cache
from typing import Any, Callable, Dict, Optional, TypeVar

from .config import config

# Set up logging
logger = logging.getLogger("graphrag_mcp")
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)


# Cache implementation
T = TypeVar('T')

class ResultCache:
    """LRU cache with TTL support."""
    
    def __init__(self, max_size: int = config.MAX_CACHE_SIZE, ttl: int = config.CACHE_TTL):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl  # seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if it exists and hasn't expired."""
        if not config.ENABLE_CACHE:
            return None
            
        if key not in self.cache:
            return None
            
        entry = self.cache[key]
        if time.time() - entry["timestamp"] > self.ttl:
            # Expired
            del self.cache[key]
            return None
            
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        if not config.ENABLE_CACHE:
            return
            
        # Use provided TTL or default
        actual_ttl = ttl if ttl is not None else self.ttl
        
        # If cache is full, remove oldest entry
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": actual_ttl
        }
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()


# Rate limiter implementation
class RateLimiter:
    """Simple rate limiter."""
    
    def __init__(self, window_ms: int = config.RATE_LIMIT_WINDOW, max_requests: int = config.RATE_LIMIT_MAX):
        self.window_ms = window_ms
        self.max_requests = max_requests
        self.requests = []
    
    def allow_request(self) -> bool:
        """Check if a request should be allowed based on rate limits."""
        now = time.time() * 1000  # Convert to milliseconds
        
        # Remove requests older than the window
        self.requests = [req for req in self.requests if now - req < self.window_ms]
        
        # Check if we've hit the limit
        if len(self.requests) >= self.max_requests:
            return False
        
        # Add this request to the list
        self.requests.append(now)
        return True


# Global instances
cache = ResultCache()
rate_limiter = RateLimiter()


def timed_execution(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure and log function execution time."""
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.debug(f"{func.__name__} executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper