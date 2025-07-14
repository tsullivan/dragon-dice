"""
Type-safe game setup helpers for testing.
Creates GameEngine instances with fully typed model data.
"""

from typing import List, Tuple, Dict, Any
from game_logic.engine import GameEngine
from models.test.mock.typed_models import create_home_army_typed, create_campaign_army_typed
from models.test.mock.player_mock import create_player_setup_dict


def create_typed_game_engine(
    player_names: List[str],
    home_terrains: List[str],
    frontier_terrain: str,
    first_player_name: str,
    distance_rolls: List[Tuple[str, int]],
) -> GameEngine:
    """
    Create a GameEngine with type-safe, complete player setup data.

    Args:
        player_names: List of player names (must match first_player_name)
        home_terrains: List of home terrain names (same length as player_names)
        frontier_terrain: Name of the frontier terrain
        first_player_name: Name of the first player (must be in player_names)
        distance_rolls: List of (entity_name, roll_value) tuples

    Returns:
        GameEngine instance with complete, validated setup data

    Raises:
        ValueError: If arguments are inconsistent
        TypeError: If arguments have wrong types (caught by mypy)
    """
    if len(player_names) != len(home_terrains):
        raise ValueError(f"Mismatch: {len(player_names)} players, {len(home_terrains)} terrains")

    if first_player_name not in player_names:
        raise ValueError(f"First player '{first_player_name}' not in player list: {player_names}")

    # Create complete player setup data using mock infrastructure
    player_setup_data = []

    for player_name, home_terrain in zip(player_names, home_terrains):
        player_data = create_player_setup_dict(
            name=player_name, home_terrain=home_terrain, frontier_terrain_proposal=frontier_terrain, force_size=24
        )
        player_setup_data.append(player_data)

    # Create GameEngine with validated parameters
    return GameEngine(
        player_setup_data=player_setup_data,
        first_player_name=first_player_name,
        frontier_terrain=frontier_terrain,
        distance_rolls=distance_rolls,
    )


def create_standard_two_player_engine(
    player1_name: str = "Player 1",
    player1_home: str = "Highland",
    player2_name: str = "Player 2",
    player2_home: str = "Coastland",
    frontier_terrain: str = "Coastland",
) -> GameEngine:
    """
    Create a standard two-player GameEngine for testing.

    All parameters are typed and have sensible defaults.
    """
    return create_typed_game_engine(
        player_names=[player1_name, player2_name],
        home_terrains=[player1_home, player2_home],
        frontier_terrain=frontier_terrain,
        first_player_name=player1_name,
        distance_rolls=[(player1_name, 3), (player2_name, 5), ("__frontier__", 4)],
    )


def create_engine_with_armies_chosen(acting_army_unique_id: str, **engine_kwargs: Any) -> GameEngine:
    """
    Create a GameEngine and advance it to have an acting army chosen.

    Args:
        acting_army_unique_id: ID of army to choose (e.g., "player_1_home")
        **engine_kwargs: Arguments to pass to create_standard_two_player_engine

    Returns:
        GameEngine with acting army already chosen and ready for maneuver/action
    """
    engine = create_standard_two_player_engine(**engine_kwargs)

    # Find and choose the specified army
    all_players_data = engine.get_all_players_data()

    for player_name, player_data in all_players_data.items():
        for army_type, army_data in player_data.get("armies", {}).items():
            if army_data.get("unique_id") == acting_army_unique_id:
                army_choice_data = {
                    "name": army_data["name"],
                    "army_type": army_type,
                    "location": army_data["location"],
                    "units": army_data["units"],
                    "unique_id": army_data["unique_id"],
                }
                engine.choose_acting_army(army_choice_data)
                return engine

    raise ValueError(f"Army with unique_id '{acting_army_unique_id}' not found")


# Type-safe validation functions


def validate_engine_state(
    engine: GameEngine, expected_player: str, expected_phase: str, expected_march_step: str
) -> None:
    """
    Type-safe validation of GameEngine state.

    Args:
        engine: GameEngine to validate (typed)
        expected_player: Expected current player name
        expected_phase: Expected current phase
        expected_march_step: Expected march step

    Raises:
        AssertionError: If any expectation is not met
    """
    actual_player = engine.get_current_player_name()
    actual_phase = engine.current_phase
    actual_step = engine.current_march_step

    assert actual_player == expected_player, f"Expected player '{expected_player}', got '{actual_player}'"
    assert actual_phase == expected_phase, f"Expected phase '{expected_phase}', got '{actual_phase}'"
    assert actual_step == expected_march_step, f"Expected step '{expected_march_step}', got '{actual_step}'"


def validate_army_data_completeness(army_data: Dict[str, Any]) -> None:
    """
    Type-safe validation that army data has all required fields.

    Args:
        army_data: Army dictionary to validate (as returned by GameStateManager)

    Raises:
        AssertionError: If required fields are missing
    """
    # Fields as they appear in actual GameEngine army data
    required_fields = ["name", "location", "units", "unique_id", "army_type"]

    for field in required_fields:
        assert field in army_data, f"Army data missing required field: {field}"
        assert army_data[field] is not None, f"Army data field '{field}' is None"

    # Validate units list
    units = army_data["units"]
    assert isinstance(units, list), f"Army units must be list, got {type(units)}"

    for i, unit in enumerate(units):
        # Unit fields as they appear in GameStateManager data
        unit_required_fields = ["unit_id", "name", "unit_type", "health", "max_health", "species"]
        for field in unit_required_fields:
            assert field in unit, f"Unit {i} missing required field: {field}"
