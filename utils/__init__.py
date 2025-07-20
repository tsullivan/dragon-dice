"""
Utility modules for the Dragon Dice digital companion app.
"""

from .field_access import MissingFieldError, strict_get, strict_get_optional, strict_get_with_fallback

__all__ = ["strict_get", "strict_get_optional", "strict_get_with_fallback", "MissingFieldError"]
