"""VeriSigil SDK Exceptions"""


class VeriSigilError(Exception):
    """Base exception for all VeriSigil SDK errors."""
    def __init__(self, message: str, status_code: int = None, detail: dict = None):
        self.message    = message
        self.status_code = status_code
        self.detail     = detail or {}
        super().__init__(message)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.message!r})"


class AuthenticationError(VeriSigilError):
    """Raised when API key is invalid or missing."""
    pass


class AdmissibilityError(VeriSigilError):
    """
    Raised when an action is ruled INADMISSIBLE.
    Contains the full governance ruling for audit purposes.
    """
    def __init__(self, message: str, ruling: dict = None):
        self.ruling = ruling or {}
        super().__init__(message, status_code=403, detail=ruling)


class RateLimitError(VeriSigilError):
    """Raised when rate limit is exceeded."""
    pass


class TimelockError(VeriSigilError):
    """Raised when a timelocked operation cannot yet execute."""
    def __init__(self, message: str, remaining_hours: float = None):
        self.remaining_hours = remaining_hours
        super().__init__(message, status_code=425)


class ValidationError(VeriSigilError):
    """Raised when request validation fails."""
    pass
