class SalimAPIGenException(Exception):
    """Base exception for SaLim-api-gen"""


class ValidationError(SalimAPIGenException):
    """Raised when input validation fails"""


class APIError(SalimAPIGenException):
    """Raised when the API returns an error"""


class RateLimitExceeded(SalimAPIGenException):
    """Raised when the rate limit is exceeded"""


class AuthenticationError(SalimAPIGenException):
    """Raised when authentication fails"""


class ConfigurationError(SalimAPIGenException):
    """Raised when there's an error in the configuration"""


class NetworkError(SalimAPIGenException):
    """Raised when there's a network-related error"""


class TimeoutError(SalimAPIGenException):
    """Raised when a request times out"""


class UnexpectedResponseError(SalimAPIGenException):
    """Raised when the API returns an unexpected response"""


class HTTPError(APIError):
    """Raised when an HTTP error occurs"""

    def __init__(self, status_code, message):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


class JSONDecodeError(APIError):
    """Raised when JSON decoding fails"""

    def __init__(self, message):
        super().__init__(f"JSON Decode Error: {message}")


class InvalidParameterError(ValidationError):
    """Raised when an invalid parameter is provided"""

    def __init__(self, parameter_name, message):
        super().__init__(f"Invalid parameter '{parameter_name}': {message}")
