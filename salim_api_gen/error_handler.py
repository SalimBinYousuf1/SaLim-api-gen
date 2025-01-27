import logging
from typing import Dict, Any, Callable
from .exceptions import APIError, HTTPError, JSONDecodeError, RateLimitExceeded


class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_callbacks: Dict[str, Callable] = {}

    def register_error_callback(self, error_type: str, callback: Callable):
        self.error_callbacks[error_type] = callback

    def handle_error(self, error: Exception, context: Dict[str, Any] = None):
        error_type = type(error).__name__
        self.logger.error(f"Error occurred: {error_type} - {str(error)}")

        if context:
            self.logger.error(f"Context: {context}")

        if error_type in self.error_callbacks:
            self.error_callbacks[error_type](error, context)

        if isinstance(error, HTTPError):
            self.logger.error(f"HTTP Status Code: {error.status_code}")
        elif isinstance(error, RateLimitExceeded):
            self.logger.warning("Rate limit exceeded. Implementing backoff strategy.")
        elif isinstance(error, JSONDecodeError):
            self.logger.error("Failed to decode JSON response.")
        elif isinstance(error, APIError):
            self.logger.error("General API error occurred.")
        else:
            self.logger.exception("An unexpected error occurred.")

        # Re-raise the error for the caller to handle
        raise error
