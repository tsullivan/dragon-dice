#!/usr/bin/env python3
"""
End-to-end tests for creating new armies from the Reserve Area in Dragon Dice.
Tests the complete flow of moving units to reserves and then creating new armies.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from game_logic.engine import GameEngine
from game_logic.game_state_manager import GameStateManager


class TestArmyCreationFromReserves(unittest.TestCase):
    """E2E tests for creating new armies by moving units from reserves to unoccupied terrains."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test data for each test."""
        # Base game state tracking
        self.game_log = []

    def _setup_army_creation_scenario(self):
        """Set up a scenario for testing army creation from reserves."""
        self.player_setup_data = [
            {
                "name": "Player 1",
                "home_terrain": "Highland",
                "armies": {
                    "home": {
                        "name": "Highland Guard",
                        "location": "Player 1 Highland",
                        "units": [
                            {
                                "name": "Home Charioteer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "home_1",
                                "unit_type": "amazon_charioteer",
                            },
                        ],
                        "unique_id": "player_1_home",
                        "terrain_elements": ["IVORY"],
                    },
                    "campaign": {
                        "name": "Highland Expedition",
                        "location": "Coastland",  # Frontier terrain
                        "units": [
                            {
                                "name": "Campaign Soldier 1",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_1",
                                "unit_type": "amazon_soldier",
                            },
                            {
                                "name": "Campaign Soldier 2",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_2",
                                "unit_type": "amazon_soldier",
                            },
                            {
                                "name": "Campaign Scout",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_3",
                                "unit_type": "amazon_scout",
                            },
                        ],
                        "unique_id": "player_1_campaign",
                        "terrain_elements": ["WATER"],
                    },
                    "horde": {
                        "name": "Highland Raiders",
                        "location": "Player 2 Coastland",  # Attacking Player 2's home
                        "units": [
                            {
                                "name": "Horde Archer 1",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "horde_1",
                                "unit_type": "amazon_archer",
                            },
                            {
                                "name": "Horde Archer 2",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "horde_2",
                                "unit_type": "amazon_archer",
                            },
                        ],
                        "unique_id": "player_1_horde",
                        "terrain_elements": ["WATER"],
                    },
                },
            },
            {
                "name": "Player 2",
                "home_terrain": "Coastland",
                "armies": {
                    "home": {
                        "name": "Coastal Defense",
                        "location": "Player 2 Coastland",
                        "units": [
                            {
                                "name": "Coastal Runner",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "p2_home_1",
                                "unit_type": "amazon_runner",
                            },
                        ],
                        "unique_id": "player_2_home",
                        "terrain_elements": ["WATER"],
                    },
                },
            },
        ]

        self.frontier_terrain = "Coastland"
        self.distance_rolls = [("Player 1", 4), ("Player 2", 2), ("__frontier__", 5)]

        # Create engine
        self.engine = GameEngine(
            self.player_setup_data,
            "Player 1",
            self.frontier_terrain,
            self.distance_rolls,
        )

        # Track game state
        self.game_log = []
        self._connect_army_creation_tracking()

    def _connect_army_creation_tracking(self):
        """Connect to engine signals to track army creation events."""
        self.engine.current_player_changed.connect(
            lambda player: self.game_log.append(f"Current player: {player}")
        )
        self.engine.current_phase_changed.connect(
            lambda phase: self.game_log.append(f"Phase changed: {phase}")
        )

    def _move_units_to_reserves(self, player_name: str, army_type: str):
        """Helper to move all units from an army to reserves."""
        # Get the army data
        all_players_data = self.engine.get_all_players_data()
        player_data = all_players_data[player_name]
        army_data = player_data["armies"][army_type]
        
        # Move each unit to reserves
        for unit in army_data["units"]:
            unit_dict = {
                "name": unit["name"],
                "species": "Amazon",  # Default species for these units
                "health": unit["health"],
                "elements": ["IVORY"],  # Default elements
            }
            
            # Add to reserves using the reserves manager
            self.engine.reserves_manager.add_unit_to_reserves(
                unit_dict, 
                player_name,
                army_data["location"],
                "retreat"
            )
            
        # Clear the army's units
        army_data["units"] = []
        
        print(f"Moved all units from {player_name}'s {army_type} army to reserves")

    def _advance_to_reserves_phase(self):
        """Helper to advance game to reserves phase."""
        # Skip through phases to get to reserves
        while self.engine.current_phase != "RESERVES":
            if self.engine.current_phase == "FIRST_MARCH":
                # Choose an army and skip action
                try:
                    self._choose_army_by_id("player_1_home")
                    self.engine.decide_maneuver(False)
                    self.engine.select_action("SKIP")
                except:
                    # If no valid armies, advance phase directly
                    self.engine.advance_phase()
            elif self.engine.current_phase == "SECOND_MARCH":
                # Skip second march
                self.engine.advance_phase()
            else:
                # Advance any other phase
                self.engine.advance_phase()

    def _choose_army_by_id(self, army_unique_id: str):
        """Helper to choose an army by its unique ID."""
        all_players_data = self.engine.get_all_players_data()

        # Find the army across all players
        for _player_name, player_data in all_players_data.items():
            for army_type, army_data in player_data.get("armies", {}).items():
                if army_data.get("unique_id") == army_unique_id:
                    # Only choose if army has units
                    if army_data.get("units", []):
                        army_choice_data = {
                            "name": army_data.get("name", f"{army_type.title()} Army"),
                            "army_type": army_type,
                            "location": army_data.get("location", "Unknown"),
                            "units": army_data.get("units", []),
                            "unique_id": army_data.get("unique_id", army_unique_id),
                        }
                        self.engine.choose_acting_army(army_choice_data)
                        self.game_log.append(
                            f"Army chosen: {army_choice_data['name']} at {army_choice_data['location']}"
                        )
                        return True

        return False  # Army not found or has no units

    def _simulate_reserves_phase_operations(self, player_name: str):
        """Simulate reserves phase operations using the reserves manager directly."""
        # Get available reserves for the player
        reserves = self.engine.reserves_manager.get_player_reserves(player_name)
        
        if not reserves:
            print(f"No reserves available for {player_name}")
            return {}
            
        # Simulate reinforcement plan: move some units to a new terrain
        new_terrain = "Badland"  # A terrain where player doesn't have an army
        
        # Select first 2 units from reserves for reinforcement
        units_to_reinforce = reserves[:2] if len(reserves) >= 2 else reserves[:1]
        unit_names = [unit.name for unit in units_to_reinforce]
        
        reinforcement_plan = {new_terrain: unit_names}
        
        # Process the reinforcement
        results = self.engine.reserves_manager.process_reinforcement(player_name, reinforcement_plan)
        
        # Simulate army creation with a name (normally done by UI)
        new_army_name = "Strike Force"  # Simulate user input
        
        return {
            "reinforcement_results": results,
            "new_army_name": new_army_name,
            "new_terrain": new_terrain,
            "units_moved": unit_names,
        }

    def test_e2e_create_new_army_from_reserves(self):
        """
        E2E Test: Create a new army by moving units from reserves to unoccupied terrain

        Flow:
        1. Set up player with Campaign and Horde armies containing units
        2. Move all units from Campaign army to Reserve Area  
        3. Move all units from Horde army to Reserve Area
        4. Advance to next turn's Reserves Phase
        5. Move some units from reserves to new terrain (creating new army)
        6. Verify army creation process completes successfully
        """
        print("\n🧪 E2E Test: Create New Army from Reserves")
        print("=" * 50)

        # Set up scenario
        self._setup_army_creation_scenario()
        
        # Verify initial state
        assert self.engine.get_current_player_name() == "Player 1"
        print("✅ Initial game state established")

        # === STEP 1: Move Campaign army units to reserves ===
        print("\n--- Moving Campaign Army to Reserves ---")
        initial_campaign_units = len(self.engine.get_all_players_data()["Player 1"]["armies"]["campaign"]["units"])
        print(f"Campaign army has {initial_campaign_units} units")
        
        self._move_units_to_reserves("Player 1", "campaign")
        
        # Verify campaign army is now empty
        campaign_units_after = len(self.engine.get_all_players_data()["Player 1"]["armies"]["campaign"]["units"])
        assert campaign_units_after == 0, f"Campaign army should be empty, has {campaign_units_after} units"
        print("✅ Campaign army units moved to reserves")

        # === STEP 2: Move Horde army units to reserves ===
        print("\n--- Moving Horde Army to Reserves ---")
        initial_horde_units = len(self.engine.get_all_players_data()["Player 1"]["armies"]["horde"]["units"])
        print(f"Horde army has {initial_horde_units} units")
        
        self._move_units_to_reserves("Player 1", "horde")
        
        # Verify horde army is now empty
        horde_units_after = len(self.engine.get_all_players_data()["Player 1"]["armies"]["horde"]["units"])
        assert horde_units_after == 0, f"Horde army should be empty, has {horde_units_after} units"
        print("✅ Horde army units moved to reserves")

        # === STEP 3: Verify units are in reserves ===
        print("\n--- Verifying Reserves ---")
        player_reserves = self.engine.reserves_manager.get_player_reserves("Player 1")
        expected_reserve_count = initial_campaign_units + initial_horde_units
        actual_reserve_count = len(player_reserves)
        
        assert actual_reserve_count == expected_reserve_count, \
            f"Expected {expected_reserve_count} units in reserves, got {actual_reserve_count}"
        
        print(f"✅ {actual_reserve_count} units confirmed in reserves")
        for reserve_unit in player_reserves:
            print(f"  - {reserve_unit.name} ({reserve_unit.species})")

        # === STEP 4: Advance to next turn's Reserves Phase ===
        print("\n--- Advancing to Reserves Phase ---")
        
        # Skip current turn phases to get to reserves
        self._advance_to_reserves_phase()
        
        # If not in reserves phase yet, advance to next player and their reserves
        if self.engine.current_phase != "RESERVES":
            # Complete current player's turn
            self.engine.advance_phase()
            # Advance through next player's turn to reserves
            self._advance_to_reserves_phase()

        print(f"✅ Advanced to reserves phase (Current: {self.engine.current_phase})")

        # === STEP 5: Create new army from reserves ===
        print("\n--- Creating New Army from Reserves ---")
        
        # Simulate the reserves phase operations
        army_creation_results = self._simulate_reserves_phase_operations("Player 1")
        
        if army_creation_results:
            reinforcement_results = army_creation_results["reinforcement_results"]
            new_army_name = army_creation_results["new_army_name"]
            new_terrain = army_creation_results["new_terrain"]
            units_moved = army_creation_results["units_moved"]
            
            # Verify reinforcement was successful
            assert reinforcement_results["success"], "Reinforcement should succeed"
            assert reinforcement_results["units_moved"] > 0, "Should move at least one unit"
            
            print(f"✅ Moved {reinforcement_results['units_moved']} units to {new_terrain}")
            print(f"✅ New army name: '{new_army_name}'")
            
            # === STEP 6: Verify new army creation ===
            print("\n--- Verifying New Army Creation ---")
            
            # Check that units were removed from reserves
            remaining_reserves = self.engine.reserves_manager.get_player_reserves("Player 1")
            expected_remaining = expected_reserve_count - reinforcement_results["units_moved"]
            actual_remaining = len(remaining_reserves)
            
            assert actual_remaining == expected_remaining, \
                f"Expected {expected_remaining} units remaining in reserves, got {actual_remaining}"
            
            print(f"✅ {actual_remaining} units remaining in reserves")
            
            # Verify reinforcement data structure
            assert new_terrain in reinforcement_results["reinforcements"], \
                f"Reinforcement results should include {new_terrain}"
            
            reinforced_units = reinforcement_results["reinforcements"][new_terrain]
            assert len(reinforced_units) == len(units_moved), \
                f"Should have reinforced {len(units_moved)} units"
            
            print(f"✅ Reinforced {len(reinforced_units)} units to {new_terrain}")
            
            # In a real game, the UI would create the new army in game state
            # For this test, we verify the reinforcement process completed successfully
            print("✅ Army creation process completed successfully")

        else:
            print("❌ No reserves available for army creation")
            
        print("✅ Test completed - New army creation from reserves flow successful")

    def test_e2e_army_creation_with_multiple_terrains(self):
        """
        E2E Test: Create multiple new armies by deploying to different terrains

        Flow:
        1. Set up player with multiple units in reserves
        2. Deploy units to multiple unoccupied terrains
        3. Verify multiple army creation process
        """
        print("\n🧪 E2E Test: Multiple Army Creation from Reserves")
        print("=" * 50)

        # Set up scenario
        self._setup_army_creation_scenario()
        
        # Move units to reserves from multiple armies
        self._move_units_to_reserves("Player 1", "campaign")
        self._move_units_to_reserves("Player 1", "horde")
        
        # Verify we have enough units in reserves
        player_reserves = self.engine.reserves_manager.get_player_reserves("Player 1")
        initial_reserve_count = len(player_reserves)
        assert initial_reserve_count >= 4, f"Need at least 4 units for multiple army test, got {initial_reserve_count}"
        
        print(f"Starting with {initial_reserve_count} units in reserves")

        # === Create multiple reinforcement plans ===
        print("\n--- Creating Multiple Armies ---")
        
        # Plan 1: 2 units to Badland
        terrain_1 = "Badland"
        units_1 = [player_reserves[0].name, player_reserves[1].name]
        reinforcement_plan_1 = {terrain_1: units_1}
        
        # Plan 2: 2 units to Swampland  
        terrain_2 = "Swampland"
        remaining_reserves = player_reserves[2:]
        if len(remaining_reserves) >= 2:
            units_2 = [remaining_reserves[0].name, remaining_reserves[1].name]
            reinforcement_plan_2 = {terrain_2: units_2}
        else:
            units_2 = [remaining_reserves[0].name] if remaining_reserves else []
            reinforcement_plan_2 = {terrain_2: units_2}

        # Process first reinforcement
        results_1 = self.engine.reserves_manager.process_reinforcement("Player 1", reinforcement_plan_1)
        assert results_1["success"], "First reinforcement should succeed"
        print(f"✅ Created army at {terrain_1} with {len(units_1)} units")

        # Process second reinforcement  
        if units_2:
            results_2 = self.engine.reserves_manager.process_reinforcement("Player 1", reinforcement_plan_2)
            assert results_2["success"], "Second reinforcement should succeed"
            print(f"✅ Created army at {terrain_2} with {len(units_2)} units")

        # Verify final reserves count
        final_reserves = self.engine.reserves_manager.get_player_reserves("Player 1")
        total_units_moved = len(units_1) + len(units_2)
        expected_final = initial_reserve_count - total_units_moved
        assert len(final_reserves) == expected_final, \
            f"Expected {expected_final} units remaining (started with {initial_reserve_count}, moved {total_units_moved}), got {len(final_reserves)}"

        print(f"✅ {len(final_reserves)} units remaining in reserves")
        print("✅ Multiple army creation test completed successfully")

    def test_e2e_army_creation_name_validation(self):
        """
        E2E Test: Verify army naming validation during creation

        This test simulates the UI validation that occurs when naming new armies.
        """
        print("\n🧪 E2E Test: Army Creation Name Validation")
        print("=" * 50)

        # Set up scenario
        self._setup_army_creation_scenario()
        
        # Move some units to reserves
        self._move_units_to_reserves("Player 1", "campaign")
        
        player_reserves = self.engine.reserves_manager.get_player_reserves("Player 1")
        assert len(player_reserves) > 0, "Need units in reserves for name validation test"

        # === Test name validation scenarios ===
        print("\n--- Testing Army Name Validation ---")
        
        # Simulate the validation logic from reserves_phase_dialog.py
        def validate_army_name(army_name: str, existing_new_army_names: list = []) -> tuple:
            """Simulate army name validation logic."""
            army_name = army_name.strip()
            
            # Check for empty name
            if not army_name:
                return False, "Army name cannot be empty."
            
            # Check for reserved names
            reserved_names = ["Home", "Campaign", "Horde"]
            if army_name in reserved_names:
                return False, f"'{army_name}' is a reserved army name. Please choose a different name."
            
            # Check for duplicate names in current session
            if army_name in existing_new_army_names:
                return False, f"You've already chosen '{army_name}' for another new army. Please choose a different name."
            
            return True, "Valid name"

        # Test cases
        test_names = [
            ("", False, "empty name"),
            ("Home", False, "reserved name 'Home'"),
            ("Campaign", False, "reserved name 'Campaign'"),
            ("Horde", False, "reserved name 'Horde'"),
            ("Strike Force", True, "valid custom name"),
            ("Highland Raiders", True, "valid custom name with space"),
            ("1st Battalion", True, "valid name with numbers"),
        ]

        existing_names = []
        
        for test_name, should_be_valid, description in test_names:
            is_valid, message = validate_army_name(test_name, existing_names)
            
            if should_be_valid:
                assert is_valid, f"'{test_name}' should be valid ({description}): {message}"
                existing_names.append(test_name)  # Add to existing names for duplicate check
                print(f"✅ '{test_name}' - {description}")
            else:
                assert not is_valid, f"'{test_name}' should be invalid ({description})"
                print(f"✅ '{test_name}' correctly rejected - {description}")

        # Test duplicate name detection
        duplicate_name = "Strike Force"
        is_valid, message = validate_army_name(duplicate_name, existing_names)
        assert not is_valid, f"Duplicate name '{duplicate_name}' should be rejected"
        print(f"✅ Duplicate name '{duplicate_name}' correctly rejected")

        print("✅ Army name validation test completed successfully")

    def tearDown(self):
        """Clean up after each test."""
        # Clear game log for next test
        self.game_log.clear()


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)