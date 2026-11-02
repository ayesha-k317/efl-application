"""Error types used across the application"""                           # Docstring: what this file is for
class EFLError(Exception):                                              # Base class; every EFL inherits from it
    """Base class for all EFL Errors"""
class InputError(EFLError):                                             # The user typed something invalid
    "The user typed something invalid. Show a clear message."""
class RateUnavailableError(EFLError):                                   # No exchange rate could be found
    """No exchange rate could be loaded."""