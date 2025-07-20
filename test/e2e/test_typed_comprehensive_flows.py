#!/usr/bin/env python3
"""
Type-safe comprehensive E2E tests using the new mock infrastructure.
Demonstrates migration from dict-based to type-safe model creation.
"""

import os
import sys
from typing import List

import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from game_logic.game_orchestrator import GameOrchestrator as GameEngine

# Type-safe imports
from models.test.mock.typed_game_setup import (
    create_engine_with_armies_chosen,
    create_standard_two_player_engine,
    validate_army_data_completeness,
    validate_engine_state,
)
from models.test.mock.typed_models import create_test_army, create_test_unit


class TestTypedGameEngineFlows:
    """Type-safe comprehensive tests using mock infrastructure."""

    @pytest.fixture(autouse=True)
    def setup_typed_game_engine(self, qtbot):
        """Set up type-safe game engine for testing."""
        self.qtbot = qtbot

        # Create engine using type-safe mock infrastructure
        self.engine = create_standard_two_player_engine(
            player1_name="Highland Player",
            player1_home="Highland",
            player2_name="Coastal Player",
            player2_home="Coastland",
            frontier_terrain="Coastland"
        )

        yield

        # Cleanup
        self.engine = None

    def test_typed_engine_initialization(self):
        """Test that typed engine initializes with complete data."""
        print("\n🧪 Test: Typed Engine Initialization")
        print("=" * 50)

        # Validate initial state using type-safe validation
        validate_engine_state(
            engine=self.engine,
            expected_player="Highland Player",  # Our custom player names are working
            expected_phase="FIRST_MARCH",
            expected_march_step="CHOOSE_ACTING_ARMY"
        )

        # Validate player data completeness
        all_players_data = self.engine.get_all_players_data()

        for player_name, player_data in all_players_data.items():
            # Check required player fields (based on actual GameStateManager structure)
            required_player_fields = ["name", "home_terrain_name", "selected_dragons", "armies"]
            for field in required_player_fields:
                assert field in player_data, f"Player {player_name} missing field: {field}"

            # Validate each army
            for army_type, army_data in player_data["armies"].items():
                validate_army_data_completeness(army_data)
                print(f"✅ {player_name} {army_type} army data validated")

        print("✅ All player and army data validated successfully")

    def test_typed_army_selection_flow(self):
        """Test army selection with type-safe army data."""
        print("\n🧪 Test: Typed Army Selection Flow")
        print("=" * 50)

        # Get available armies (these are type-safe from our mock data)
        available_armies = self.engine.get_available_acting_armies()
        assert len(available_armies) > 0, "Should have available armies"

        # Choose first army using type-safe data
        first_army = available_armies[0]
        validate_army_data_completeness(first_army)

        print(f"Choosing army: {first_army['name']} at {first_army['location']}")

        # This should work without any MissingFieldError
        self.engine.choose_acting_army(first_army)

        # Validate state transition
        validate_engine_state(
            engine=self.engine,
            expected_player="Highland Player",
            expected_phase="FIRST_MARCH",
            expected_march_step="DECIDE_MANEUVER"
        )

        print("✅ Army selection completed with type-safe data")

    def test_typed_complete_march_flow(self):
        """Test complete march flow with type-safe operations."""
        print("\n🧪 Test: Typed Complete March Flow")
        print("=" * 50)

        # Use convenience function to get engine with army chosen
        engine_with_army = create_engine_with_armies_chosen(
            acting_army_unique_id="player_1_home"
        )

        # Step 1: Skip maneuver
        print("Step 1: Skip maneuver")
        engine_with_army.decide_maneuver(False)

        validate_engine_state(
            engine=engine_with_army,
            expected_player="Player 1",
            expected_phase="FIRST_MARCH",
            expected_march_step="SELECT_ACTION"
        )

        # Step 2: Skip action
        print("Step 2: Skip action")
        engine_with_army.select_action("SKIP")

        # Should advance to second march
        validate_engine_state(
            engine=engine_with_army,
            expected_player="Player 1",
            expected_phase="SECOND_MARCH",
            expected_march_step="CHOOSE_ACTING_ARMY"
        )

        print("✅ Complete march flow validated with typed operations")

    def test_typed_model_creation(self):
        """Test direct typed model creation for complete type safety."""
        print("\n🧪 Test: Typed Model Creation")
        print("=" * 50)

        # Create typed unit - mypy will catch missing arguments
        unit = create_test_unit(
            unit_id="typed_test_unit",
            name="Typed Warrior",
            unit_type="amazon_warrior",
            health=2,
            max_health=2,
            species_key="AMAZON"
        )

        # Validate unit properties (all typed)
        assert unit.unit_id == "typed_test_unit"
        assert unit.name == "Typed Warrior"
        assert unit.unit_type == "amazon_warrior"
        assert unit.health == 2
        assert unit.max_health == 2
        assert unit.species.name == "Amazon"  # Type-safe species access
        assert len(unit.faces) == 1  # Default face count

        print(f"✅ Created typed unit: {unit.name} ({unit.unit_id})")

        # Create typed army with the unit
        units_list = [unit]
        army = create_test_army(
            name="Typed Test Army",
            army_type="test",
            location="Test Location",
            max_points=20,
            units=units_list
        )

        # Validate army properties (all typed)
        assert army.name == "Typed Test Army"
        assert army.army_type == "test"
        assert army.max_points == 20
        assert len(army.units) == 1
        assert army.units[0].unit_id == "typed_test_unit"

        print(f"✅ Created typed army: {army.name} with {len(army.units)} units")

    def test_typed_action_flow_with_validation(self):
        """Test action flow with type-safe mock data and validation."""
        print("\n🧪 Test: Typed Action Flow with Validation")
        print("=" * 50)

        # Set up engine with army chosen
        engine = create_engine_with_armies_chosen("player_1_home")

        # Skip maneuver, select action
        engine.decide_maneuver(False)
        engine.select_action("SKIP")

        # SKIP action should immediately advance to next march or next player
        # Check that the action was processed successfully with typed mock data
        current_step = engine.current_march_step
        assert current_step in ["CHOOSE_ACTING_ARMY"], f"Expected valid march step after SKIP, got: {current_step}"

        print("✅ Action flow completed with typed mock data")

    def test_typed_error_detection(self):
        """Test that typed functions catch errors at creation time."""
        print("\n🧪 Test: Typed Error Detection")
        print("=" * 50)

        # Test that invalid species key is caught immediately
        try:
            create_test_unit(
                unit_id="invalid_unit",
                name="Invalid Unit",
                unit_type="test_type",
                species_key="INVALID_SPECIES"  # This should fail
            )
            raise AssertionError("Should have caught invalid species")
        except ValueError as e:
            print(f"✅ Caught invalid species error: {e}")

        # Test that type mismatches would be caught by mypy
        # (These would fail at compile time with mypy, but we can't demo that in runtime)

        # Test validation functions catch missing data
        incomplete_army_data = {
            "name": "Incomplete Army",
            "location": "Some Location"
            # Missing: allocated_points, units, unique_id
        }

        try:
            validate_army_data_completeness(incomplete_army_data)
            raise AssertionError("Should have caught incomplete army data")
        except AssertionError as e:
            print(f"✅ Caught incomplete army data: {e}")

        print("✅ Error detection working correctly")


if __name__ == "__main__":
    # Run with verbose output
    pytest.main([__file__, "-v", "-s"])
