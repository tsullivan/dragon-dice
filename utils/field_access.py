"""
Strict field access utilities for Dragon Dice models.

This module provides utilities to enforce fail-fast behavior when accessing
model fields, replacing lenient patterns like `dict.get(key, default)` with
strict field access that raises errors when required fields are missing.
"""

from typing import Any, Dict, TypeVar, Union

T = TypeVar('T')


class MissingFieldError(Exception):
    """Raised when a required field is missing from a model."""
    
    def __init__(self, field_name: str, model_name: str = "model"):
        super().__init__(f"Required field '{field_name}' is missing from {model_name}")
        self.field_name = field_name
        self.model_name = model_name


def strict_get(data: Dict[str, Any], field_name: str, model_name: str = "model") -> Any:
    """
    Strictly access a field from a model dictionary.
    
    Args:
        data: The model dictionary to access
        field_name: The field name to retrieve
        model_name: Optional name of the model for better error messages
        
    Returns:
        The field value
        
    Raises:
        MissingFieldError: If the field is missing or None
    """
    if field_name not in data:
        raise MissingFieldError(field_name, model_name)
    
    value = data[field_name]
    if value is None:
        raise MissingFieldError(field_name, model_name)
        
    return value


def strict_get_optional(data: Dict[str, Any], field_name: str, default: T = None) -> Union[Any, T]:
    """
    Access a field that is genuinely optional.
    
    Use this sparingly, only for fields that are truly optional by design.
    Most fields should use strict_get() instead.
    
    Args:
        data: The model dictionary to access
        field_name: The field name to retrieve
        default: Default value if field is missing or None
        
    Returns:
        The field value or default
    """
    return data.get(field_name, default)


def strict_get_with_fallback(data: Dict[str, Any], field_name: str, fallback_field: str, model_name: str = "model") -> Any:
    """
    Strictly access a field with a fallback to another field.
    
    This is for cases where there are multiple valid field names for the same data,
    such as legacy field names or format variations.
    
    Args:
        data: The model dictionary to access
        field_name: The primary field name to retrieve
        fallback_field: The fallback field name if primary is missing
        model_name: Optional name of the model for better error messages
        
    Returns:
        The field value from either primary or fallback field
        
    Raises:
        MissingFieldError: If both fields are missing or None
    """
    # Try primary field first
    if field_name in data and data[field_name] is not None:
        return data[field_name]
    
    # Try fallback field
    if fallback_field in data and data[fallback_field] is not None:
        return data[fallback_field]
    
    # Neither field exists or both are None
    raise MissingFieldError(f"{field_name} (or fallback {fallback_field})", model_name)