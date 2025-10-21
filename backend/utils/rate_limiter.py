"""
Simple in-memory rate limiter for login attempts.
Tracks failed login attempts per email/IP combination.
Limit: 5 attempts per 6 hours
"""

from datetime import datetime, timedelta
from collections import defaultdict
import threading


class LoginRateLimiter:
    """
    In-memory rate limiter for login attempts.
    Thread-safe implementation using locks.
    """
    
    def __init__(self):
        """Initialize rate limiter with empty tracking dict and lock."""
        # Structure: {email:ip: [(timestamp1, timestamp2, ...)]}
        self._attempts = defaultdict(list)
        self._lock = threading.Lock()
        
        # Rate limit configuration
        self.MAX_ATTEMPTS = 5
        self.LOCKOUT_HOURS = 6
    
    def is_rate_limited(self, email, ip_address):
        """
        Check if the email/IP combination is rate limited.
        
        Args:
            email: User email address
            ip_address: IP address of the request
            
        Returns:
            tuple: (is_limited: bool, attempts_remaining: int, reset_time: datetime or None)
        """
        with self._lock:
            key = f"{email}:{ip_address}"
            attempts = self._attempts[key]
            
            # Remove attempts older than 6 hours
            cutoff_time = datetime.now() - timedelta(hours=self.LOCKOUT_HOURS)
            attempts = [attempt_time for attempt_time in attempts if attempt_time > cutoff_time]
            self._attempts[key] = attempts
            
            # Check if rate limited
            if len(attempts) >= self.MAX_ATTEMPTS:
                # Find the oldest attempt to calculate when it expires
                oldest_attempt = min(attempts)
                reset_time = oldest_attempt + timedelta(hours=self.LOCKOUT_HOURS)
                return True, 0, reset_time
            
            # Not rate limited
            attempts_remaining = self.MAX_ATTEMPTS - len(attempts)
            return False, attempts_remaining, None
    
    def record_failed_attempt(self, email, ip_address):
        """
        Record a failed login attempt.
        
        Args:
            email: User email address
            ip_address: IP address of the request
        """
        with self._lock:
            key = f"{email}:{ip_address}"
            self._attempts[key].append(datetime.now())
    
    def clear_attempts(self, email, ip_address):
        """
        Clear all failed attempts for an email/IP (called on successful login).
        
        Args:
            email: User email address
            ip_address: IP address of the request
        """
        with self._lock:
            key = f"{email}:{ip_address}"
            if key in self._attempts:
                del self._attempts[key]
    
    def cleanup_old_attempts(self):
        """
        Cleanup attempts older than lockout period.
        Should be called periodically to free memory.
        """
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=self.LOCKOUT_HOURS)
            
            # Clean up old attempts
            keys_to_remove = []
            for key, attempts in self._attempts.items():
                # Filter out old attempts
                recent_attempts = [t for t in attempts if t > cutoff_time]
                
                if recent_attempts:
                    self._attempts[key] = recent_attempts
                else:
                    keys_to_remove.append(key)
            
            # Remove empty entries
            for key in keys_to_remove:
                del self._attempts[key]
    
    def get_stats(self):
        """
        Get rate limiter statistics (for monitoring).
        
        Returns:
            dict: Statistics about current rate limiting state
        """
        with self._lock:
            total_tracked = len(self._attempts)
            total_attempts = sum(len(attempts) for attempts in self._attempts.values())
            
            return {
                'tracked_users': total_tracked,
                'total_attempts': total_attempts,
                'max_attempts_allowed': self.MAX_ATTEMPTS,
                'lockout_hours': self.LOCKOUT_HOURS
            }


# Global rate limiter instance
login_rate_limiter = LoginRateLimiter()

