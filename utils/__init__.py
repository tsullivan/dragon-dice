"""
Utility modules for the Dragon Dice digital companion app.
"""

from .field_access import strict_get, strict_get_optional, strict_get_with_fallback, MissingFieldError

__all__ = ["strict_get", "strict_get_optional", "strict_get_with_fallback", "MissingFieldError"]
