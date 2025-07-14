"""
Example usage of the mock data infrastructure.
Shows how to replace incomplete test data with type-safe mocks.
"""

from models.test.mock import create_unit_dict, create_army_dict, create_player_setup_dict, create_two_player_setup

# === BEFORE: Incomplete test data (causes runtime errors) ===


def bad_test_setup():
    """Example of problematic test data that strict accessors will catch."""
    # Missing required fields - will cause MissingFieldError
    incomplete_unit = {
        "name": "Warrior",
        "health": 2,
        "max_health": 2,
        # Missing: unit_id, unit_type, species, faces
    }

    incomplete_army = {
        "name": "Test Army",
        "location": "Highland",
        # Missing: allocated_points, units, unique_id
    }

    incomplete_player = {
        "name": "Player 1",
        "home_terrain": "Highland",
        # Missing: force_size, selected_dragons, armies
    }

    return incomplete_player  # This will fail with strict accessors


# === AFTER: Complete test data using mocks ===


def good_test_setup():
    """Example of proper test data using mock infrastructure."""

    # Create complete unit data
    unit = create_unit_dict(
        unit_id="warrior_1", name="Highland Warrior", unit_type="amazon_warrior", health=2, max_health=2
    )

    # Create complete army data
    army = create_army_dict(
        name="Highland Guard",
        location="Player 1 Highland",
        allocated_points=10,
        unique_id="player_1_home",
        unit_count=3,
    )

    # Create complete player data
    player = create_player_setup_dict(name="Player 1", home_terrain="Highland", force_size=24)

    return player  # This will work with strict accessors


# === ADVANCED: Two-player game setup ===


def create_test_game_setup():
    """Create a complete two-player game setup for E2E tests."""

    # Use the two-player convenience function
    players = create_two_player_setup(
        player1_name="Highland Player",
        player1_home="Highland",
        player2_name="Coastal Player",
        player2_home="Coastland",
        frontier_terrain="Coastland",
    )

    # Standard distance rolls for testing
    distance_rolls = [("Highland Player", 3), ("Coastal Player", 5), ("__frontier__", 4)]

    return {
        "players": players,
        "frontier_terrain": "Coastland",
        "distance_rolls": distance_rolls,
        "first_player": "Highland Player",
    }


# === TYPE-SAFE: Direct model instantiation ===


def create_test_models():
    """Example of creating model instances directly (fully type-checked)."""
    from models.test.mock.unit_mock import create_unit_instance
    from game_logic.engine import GameEngine

    # This is fully type-checked - missing arguments will be caught by mypy
    unit = create_unit_instance(
        unit_id="test_unit",
        name="Test Warrior",
        unit_type="amazon_warrior",
        health=1,
        max_health=1,
        species_name="Amazon",
    )

    # Create game engine with complete data
    game_setup = create_test_game_setup()
    engine = GameEngine(
        player_setup_data=game_setup["players"],
        first_player=game_setup["first_player"],
        frontier_terrain=game_setup["frontier_terrain"],
        distance_rolls=game_setup["distance_rolls"],
    )

    return unit, engine


if __name__ == "__main__":
    # Demonstrate the difference
    print("=== Bad setup (would fail with strict accessors) ===")
    try:
        bad_data = bad_test_setup()
        print("Bad data created (but would fail when used)")
    except Exception as e:
        print(f"Failed: {e}")

    print("\n=== Good setup (works with strict accessors) ===")
    good_data = good_test_setup()
    print(f"Good data created: {good_data['name']} with {len(good_data['armies'])} armies")

    print("\n=== Complete game setup ===")
    game_data = create_test_game_setup()
    print(f"Game setup: {len(game_data['players'])} players, frontier: {game_data['frontier_terrain']}")
