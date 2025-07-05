"""
Performance optimization utilities
"""
import asyncio
import time
import functools
from typing import Any, Callable, Optional, Dict
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

# Thread pool for CPU-bound operations
thread_pool = ThreadPoolExecutor(max_workers=4)


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, operation: str, duration: float):
        """Record a performance metric"""
        if operation not in self.metrics:
            self.metrics[operation] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'avg_time': 0
            }
        
        metric = self.metrics[operation]
        metric['count'] += 1
        metric['total_time'] += duration
        metric['min_time'] = min(metric['min_time'], duration)
        metric['max_time'] = max(metric['max_time'], duration)
        metric['avg_time'] = metric['total_time'] / metric['count']
    
    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get all performance metrics"""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics.clear()


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


def timed_operation(operation_name: str):
    """Decorator to time function execution"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                perf_monitor.record_metric(operation_name, duration)
                if duration > 1.0:  # Log slow operations
                    logger.warning(f"Slow operation '{operation_name}': {duration:.2f}s")
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                perf_monitor.record_metric(operation_name, duration)
                if duration > 1.0:  # Log slow operations
                    logger.warning(f"Slow operation '{operation_name}': {duration:.2f}s")
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def cache_result(ttl: int = 300, max_size: int = 100):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        max_size: Maximum cache size
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        def get_cache_key(*args, **kwargs):
            """Generate cache key from function arguments"""
            key_data = {
                'args': args,
                'kwargs': kwargs
            }
            key_str = json.dumps(key_data, sort_keys=True)
            return hashlib.md5(key_str.encode()).hexdigest()
        
        def clean_expired():
            """Remove expired cache entries"""
            current_time = time.time()
            expired_keys = [
                key for key, cache_time in cache_times.items()
                if current_time - cache_time > ttl
            ]
            for key in expired_keys:
                del cache[key]
                del cache_times[key]
        
        def enforce_size_limit():
            """Remove oldest entries if cache is too large"""
            if len(cache) > max_size:
                # Remove oldest 10% of entries
                sorted_keys = sorted(cache_times.items(), key=lambda x: x[1])
                keys_to_remove = [k for k, _ in sorted_keys[:max_size // 10]]
                for key in keys_to_remove:
                    del cache[key]
                    del cache_times[key]
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = get_cache_key(*args, **kwargs)
            
            # Clean expired entries
            clean_expired()
            
            # Check cache
            if cache_key in cache:
                logger.debug(f"Cache hit for {func.__name__}")
                return cache[cache_key]
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache[cache_key] = result
            cache_times[cache_key] = time.time()
            
            # Enforce size limit
            enforce_size_limit()
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = get_cache_key(*args, **kwargs)
            
            # Clean expired entries
            clean_expired()
            
            # Check cache
            if cache_key in cache:
                logger.debug(f"Cache hit for {func.__name__}")
                return cache[cache_key]
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache[cache_key] = result
            cache_times[cache_key] = time.time()
            
            # Enforce size limit
            enforce_size_limit()
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class ConnectionPool:
    """Generic connection pool for database connections"""
    
    def __init__(self, create_connection: Callable, max_size: int = 10):
        self.create_connection = create_connection
        self.max_size = max_size
        self.pool = asyncio.Queue(maxsize=max_size)
        self.size = 0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a connection from the pool"""
        # Try to get from pool
        try:
            return await asyncio.wait_for(self.pool.get(), timeout=0.1)
        except asyncio.TimeoutError:
            pass
        
        # Create new connection if pool not full
        async with self._lock:
            if self.size < self.max_size:
                conn = await self.create_connection()
                self.size += 1
                return conn
        
        # Wait for available connection
        return await self.pool.get()
    
    async def release(self, conn):
        """Release a connection back to the pool"""
        await self.pool.put(conn)
    
    async def close_all(self):
        """Close all connections in the pool"""
        while not self.pool.empty():
            conn = await self.pool.get()
            if hasattr(conn, 'close'):
                await conn.close()


def batch_process(items: list, batch_size: int = 10):
    """
    Process items in batches for better performance
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
    
    Yields:
        Batches of items
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


async def run_in_thread(func: Callable, *args, **kwargs) -> Any:
    """Run a blocking function in a thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(thread_pool, func, *args, **kwargs)


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int):
        """
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait if necessary to respect rate limit"""
        async with self._lock:
            now = time.time()
            
            # Remove old calls outside the time window
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            # If at limit, wait
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    # Recursive call after waiting
                    return await self.acquire()
            
            # Record this call
            self.calls.append(now)


# Performance optimization settings
OPTIMIZATION_CONFIG = {
    'enable_caching': True,
    'cache_ttl': 300,  # 5 minutes
    'max_cache_size': 1000,
    'connection_pool_size': 20,
    'batch_size': 50,
    'rate_limit_calls': 100,
    'rate_limit_window': 60  # 1 minute
}