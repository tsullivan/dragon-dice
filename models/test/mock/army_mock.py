"""
Mock data helpers for Army testing.
Provides type-safe mock data generation for army-related tests.
"""

from typing import Any, Dict, List, Optional

from models.test.mock.unit_mock import create_army_units_list, create_unit_dict


def create_army_dict(
    name: str = "Test Army",
    location: str = "Test Location",
    allocated_points: int = 10,
    army_type: str = "home",
    unique_id: Optional[str] = None,
    unit_count: int = 2,
    **extra_fields: Any,
) -> Dict[str, Any]:
    """
    Create a complete army dictionary with all required fields.

    Args:
        name: Army display name
        location: Where the army is positioned
        allocated_points: Points allocated to this army
        army_type: Type of army (home, campaign, horde)
        unique_id: Unique identifier (auto-generated if None)
        unit_count: Number of units to include
        **extra_fields: Additional fields to include

    Returns:
        Complete army dictionary for use in tests
    """
    if unique_id is None:
        unique_id = f"test_{army_type}_army"

    army_dict = {
        "name": name,
        "location": location,
        "allocated_points": allocated_points,
        "units": create_army_units_list(count=unit_count, base_name=f"{army_type.title()} Unit"),
        "unique_id": unique_id,
    }

    # Add any extra fields
    army_dict.update(extra_fields)

    return army_dict


def create_home_army_dict(
    player_name: str = "Test Player", terrain_name: str = "Highland", **kwargs: Any
) -> Dict[str, Any]:
    """Create a home army dictionary."""
    return create_army_dict(
        name=f"{terrain_name} Guard",
        location=f"{player_name} {terrain_name}",
        army_type="home",
        unique_id=f"{player_name.lower().replace(' ', '_')}_home",
        **kwargs,
    )


def create_campaign_army_dict(frontier_terrain: str = "Coastland", **kwargs: Any) -> Dict[str, Any]:
    """Create a campaign army dictionary."""
    return create_army_dict(
        name="Expeditionary Force", location=frontier_terrain, army_type="campaign", unique_id="test_campaign", **kwargs
    )


def create_horde_army_dict(target_location: str = "Enemy Territory", **kwargs: Any) -> Dict[str, Any]:
    """Create a horde army dictionary."""
    return create_army_dict(
        name="Raiders", location=target_location, army_type="horde", unique_id="test_horde", **kwargs
    )


def create_player_armies_dict(
    player_name: str = "Test Player",
    home_terrain: str = "Highland",
    frontier_terrain: str = "Coastland",
    include_horde: bool = True,
) -> Dict[str, Dict[str, Any]]:
    """
    Create a complete armies dictionary for a player.

    Returns:
        Dictionary with 'home', 'campaign', and optionally 'horde' armies
    """
    armies = {
        "home": create_home_army_dict(player_name=player_name, terrain_name=home_terrain),
        "campaign": create_campaign_army_dict(frontier_terrain=frontier_terrain),
    }

    if include_horde:
        armies["horde"] = create_horde_army_dict(target_location="Enemy Territory")

    return armies


def create_minimal_army_dict(unique_id: str = "minimal_army") -> Dict[str, Any]:
    """Create a minimal but complete army dictionary."""
    return create_army_dict(unique_id=unique_id, unit_count=1)
