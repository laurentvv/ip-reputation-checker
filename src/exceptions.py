"""
Custom exceptions for IP Reputation Checker.

This module defines custom exception classes used throughout the IP
reputation checking application.
"""

class IPReputationError(Exception):
    """Base exception for IP reputation checker."""


class RateLimitExceededError(IPReputationError):
    """Exception raised when API rate limit is exceeded."""


class InvalidIPAddressError(IPReputationError):
    """Exception raised when an IP address is invalid."""


class DatabaseError(IPReputationError):
    """Exception raised when a database operation fails."""


class AIServiceError(IPReputationError):
    """Exception raised when the AI service fails."""