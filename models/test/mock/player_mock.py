"""
Mock data helpers for Player setup testing.
Provides type-safe mock data generation for player-related tests.
"""

from typing import Any, Dict, List, Optional

from models.test.mock.army_mock import create_player_armies_dict


def create_player_setup_dict(
    name: str = "Test Player",
    home_terrain: str = "Highland",
    force_size: int = 24,
    frontier_terrain_proposal: Optional[str] = None,
    selected_dragons: Optional[List[Dict[str, str]]] = None,
    **extra_fields: Any,
) -> Dict[str, Any]:
    """
    Create a complete player setup dictionary with all required fields.

    Args:
        name: Player name
        home_terrain: Player's home terrain type
        force_size: Total force size for the player
        frontier_terrain_proposal: Proposed frontier terrain (optional)
        selected_dragons: List of selected dragons (optional)
        **extra_fields: Additional fields to include

    Returns:
        Complete player setup dictionary for GameEngine initialization
    """
    if selected_dragons is None:
        selected_dragons = []

    player_dict = {
        "name": name,
        "home_terrain": home_terrain,
        "force_size": force_size,
        "selected_dragons": selected_dragons,
        "armies": create_player_armies_dict(
            player_name=name, home_terrain=home_terrain, frontier_terrain=frontier_terrain_proposal or "Coastland"
        ),
    }

    # Add frontier proposal if provided
    if frontier_terrain_proposal:
        player_dict["frontier_terrain_proposal"] = frontier_terrain_proposal

    # Add any extra fields
    player_dict.update(extra_fields)

    return player_dict


def create_two_player_setup(
    player1_name: str = "Player 1",
    player1_home: str = "Highland",
    player2_name: str = "Player 2",
    player2_home: str = "Coastland",
    frontier_terrain: str = "Coastland",
) -> List[Dict[str, Any]]:
    """
    Create a standard two-player setup for testing.

    Returns:
        List of two complete player setup dictionaries
    """
    return [
        create_player_setup_dict(
            name=player1_name, home_terrain=player1_home, frontier_terrain_proposal=frontier_terrain
        ),
        create_player_setup_dict(
            name=player2_name, home_terrain=player2_home, frontier_terrain_proposal=frontier_terrain
        ),
    ]


def create_player_with_dragons(
    name: str = "Dragon Player", dragon_types: Optional[List[str]] = None, **kwargs: Any
) -> Dict[str, Any]:
    """
    Create a player setup with selected dragons.

    Args:
        name: Player name
        dragon_types: List of dragon type names to include
        **kwargs: Other player setup arguments

    Returns:
        Player setup dictionary with dragons
    """
    if dragon_types is None:
        dragon_types = ["Red Dragon", "Blue Dragon"]

    selected_dragons = [{"dragon_type": dragon_type, "die_type": "Drake"} for dragon_type in dragon_types]

    return create_player_setup_dict(name=name, selected_dragons=selected_dragons, **kwargs)


def create_minimal_player_setup(name: str = "Minimal Player") -> Dict[str, Any]:
    """Create a minimal but complete player setup."""
    return create_player_setup_dict(name=name)
