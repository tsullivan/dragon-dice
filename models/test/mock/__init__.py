"""
Mock data infrastructure for Dragon Dice testing.

This package provides type-safe mock data generators that ensure all required fields
are present and properly structured for testing purposes.

Usage:
    from models.test.mock.unit_mock import create_unit_dict, create_unit_instance
    from models.test.mock.army_mock import create_army_dict, create_player_armies_dict
    from models.test.mock.player_mock import create_player_setup_dict, create_two_player_setup

Benefits:
    - Type-safe: Catches missing fields at creation time
    - Complete: All required fields are included by default
    - Flexible: Easy to customize for specific test needs
    - Consistent: Reduces test data duplication and errors
"""

# Re-export commonly used mock functions for convenience
from .unit_mock import create_unit_dict, create_unit_instance, create_minimal_unit_dict, create_army_units_list

from .army_mock import (
    create_army_dict,
    create_home_army_dict,
    create_campaign_army_dict,
    create_horde_army_dict,
    create_player_armies_dict,
    create_minimal_army_dict,
)

from .player_mock import (
    create_player_setup_dict,
    create_two_player_setup,
    create_player_with_dragons,
    create_minimal_player_setup,
)

__all__ = [
    # Unit mocks
    "create_unit_dict",
    "create_unit_instance",
    "create_minimal_unit_dict",
    "create_army_units_list",
    # Army mocks
    "create_army_dict",
    "create_home_army_dict",
    "create_campaign_army_dict",
    "create_horde_army_dict",
    "create_player_armies_dict",
    "create_minimal_army_dict",
    # Player mocks
    "create_player_setup_dict",
    "create_two_player_setup",
    "create_player_with_dragons",
    "create_minimal_player_setup",
]
