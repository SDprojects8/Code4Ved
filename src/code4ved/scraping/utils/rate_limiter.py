"""Rate limiting utilities for web scraping."""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Optional


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""
    
    @abstractmethod
    async def acquire(self) -> None:
        """Acquire permission to make a request.
        
        This method will block until permission is granted.
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> dict:
        """Get rate limiter statistics.
        
        Returns:
            Dictionary of statistics
        """
        pass


class TokenBucketRateLimiter(RateLimiter):
    """Token bucket rate limiter implementation.
    
    Allows bursts of requests up to the bucket capacity while maintaining
    the average rate over time.
    """
    
    def __init__(self, rate: float, capacity: int = 5):
        """Initialize rate limiter.
        
        Args:
            rate: Requests per second
            capacity: Maximum burst capacity (bucket size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = asyncio.Lock()
        
        # Statistics
        self.total_requests = 0
        self.blocked_requests = 0
        self.total_wait_time = 0.0
    
    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        async with self._lock:
            now = time.time()
            
            # Add tokens based on elapsed time
            elapsed = now - self.last_update
            tokens_to_add = elapsed * self.rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_update = now
            
            # Check if we have tokens available
            if self.tokens >= 1:
                self.tokens -= 1
                self.total_requests += 1
            else:
                # Calculate wait time
                wait_time = (1 - self.tokens) / self.rate
                self.blocked_requests += 1
                self.total_wait_time += wait_time
                
                # Wait for tokens
                await asyncio.sleep(wait_time)
                
                # Update tokens after waiting
                self.tokens = 0
                self.total_requests += 1
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'rate': self.rate,
            'capacity': self.capacity,
            'current_tokens': self.tokens,
            'total_requests': self.total_requests,
            'blocked_requests': self.blocked_requests,
            'total_wait_time': self.total_wait_time,
            'average_wait_time': (
                self.total_wait_time / self.blocked_requests 
                if self.blocked_requests > 0 else 0
            )
        }


class FixedRateLimiter(RateLimiter):
    """Fixed rate limiter with constant delay between requests."""
    
    def __init__(self, rate: float):
        """Initialize rate limiter.
        
        Args:
            rate: Requests per second
        """
        self.rate = rate
        self.interval = 1.0 / rate
        self.last_request = 0.0
        self._lock = asyncio.Lock()
        
        # Statistics
        self.total_requests = 0
        self.total_wait_time = 0.0
    
    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_request
            
            if elapsed < self.interval:
                wait_time = self.interval - elapsed
                self.total_wait_time += wait_time
                await asyncio.sleep(wait_time)
            
            self.last_request = time.time()
            self.total_requests += 1
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'rate': self.rate,
            'interval': self.interval,
            'total_requests': self.total_requests,
            'total_wait_time': self.total_wait_time,
            'average_wait_time': (
                self.total_wait_time / self.total_requests 
                if self.total_requests > 0 else 0
            )
        }


class AdaptiveRateLimiter(RateLimiter):
    """Adaptive rate limiter that adjusts based on server responses."""
    
    def __init__(self, initial_rate: float = 1.0, max_rate: float = 10.0, 
                 min_rate: float = 0.1, capacity: int = 10):
        """Initialize adaptive rate limiter.
        
        Args:
            initial_rate: Initial requests per second
            max_rate: Maximum requests per second
            min_rate: Minimum requests per second
            capacity: Token bucket capacity
        """
        self.initial_rate = initial_rate
        self.max_rate = max_rate
        self.min_rate = min_rate
        self.capacity = capacity
        
        self.current_rate = initial_rate
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = asyncio.Lock()
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.rate_limited_requests = 0
        self.total_wait_time = 0.0
    
    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        async with self._lock:
            now = time.time()
            
            # Add tokens based on current rate
            elapsed = now - self.last_update
            tokens_to_add = elapsed * self.current_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_update = now
            
            # Check if we have tokens available
            if self.tokens >= 1:
                self.tokens -= 1
                self.total_requests += 1
            else:
                # Calculate wait time
                wait_time = (1 - self.tokens) / self.current_rate
                self.total_wait_time += wait_time
                
                # Wait for tokens
                await asyncio.sleep(wait_time)
                
                # Update tokens after waiting
                self.tokens = 0
                self.total_requests += 1
    
    def report_success(self) -> None:
        """Report a successful request."""
        self.successful_requests += 1
        
        # Increase rate slightly on success
        self.current_rate = min(self.max_rate, self.current_rate * 1.1)
    
    def report_rate_limit(self) -> None:
        """Report a rate limit response."""
        self.rate_limited_requests += 1
        
        # Decrease rate significantly on rate limit
        self.current_rate = max(self.min_rate, self.current_rate * 0.5)
    
    def report_error(self) -> None:
        """Report a request error."""
        # Decrease rate slightly on error
        self.current_rate = max(self.min_rate, self.current_rate * 0.9)
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics.
        
        Returns:
            Dictionary of statistics
        """
        success_rate = (
            self.successful_requests / self.total_requests 
            if self.total_requests > 0 else 0
        )
        
        return {
            'current_rate': self.current_rate,
            'initial_rate': self.initial_rate,
            'max_rate': self.max_rate,
            'min_rate': self.min_rate,
            'capacity': self.capacity,
            'current_tokens': self.tokens,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'rate_limited_requests': self.rate_limited_requests,
            'success_rate': success_rate,
            'total_wait_time': self.total_wait_time,
            'average_wait_time': (
                self.total_wait_time / self.total_requests 
                if self.total_requests > 0 else 0
            )
        }
