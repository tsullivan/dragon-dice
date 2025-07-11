#!/usr/bin/env python3
"""
End-to-end tests for terrain and army interaction scenarios.
Tests complex interactions between armies, terrains, and game state.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from game_logic.engine import GameEngine
from game_logic.game_state_manager import GameStateManager


class TestTerrainArmyInteractions(unittest.TestCase):
    """E2E tests for terrain and army interaction scenarios."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test data for each test."""
        self.player_setup_data = [
            {
                "name": "Player 1",
                "home_terrain": "Highland",
                "armies": {
                    "home": {
                        "name": "Home Army",
                        "location": "Player 1 Highland",
                        "units": [
                            {
                                "name": "Charioteer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "home_1",
                                "unit_type": "amazon_charioteer",
                            },
                            {
                                "name": "Charioteer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "home_2",
                                "unit_type": "amazon_charioteer",
                            },
                        ],
                        "unique_id": "player_1_home",
                    },
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Coastland",  # Frontier terrain
                        "units": [
                            {
                                "name": "Soldier",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_1",
                                "unit_type": "amazon_soldier",
                            },
                            {
                                "name": "Soldier",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_2",
                                "unit_type": "amazon_soldier",
                            },
                        ],
                        "unique_id": "player_1_campaign",
                    },
                },
            },
            {
                "name": "Player 2",
                "home_terrain": "Coastland",
                "armies": {
                    "home": {
                        "name": "Home Army",
                        "location": "Player 2 Coastland",
                        "units": [
                            {
                                "name": "Runner",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "home_p2_1",
                                "unit_type": "amazon_runner",
                            },
                            {
                                "name": "Runner",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "home_p2_2",
                                "unit_type": "amazon_runner",
                            },
                        ],
                        "unique_id": "player_2_home",
                    },
                    "horde": {
                        "name": "Horde Army",
                        "location": "Player 1 Highland",  # Invading Player 1's home
                        "units": [
                            {
                                "name": "Seer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "horde_p2_1",
                                "unit_type": "amazon_seer",
                            },
                            {
                                "name": "Seer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "horde_p2_2",
                                "unit_type": "amazon_seer",
                            },
                        ],
                        "unique_id": "player_2_horde",
                    },
                },
            },
        ]

        self.frontier_terrain = "Coastland"
        self.distance_rolls = [("Player 1", 3), ("Player 2", 5), ("__frontier__", 4)]

        # Create game engine
        self.engine = GameEngine(
            self.player_setup_data,
            "Player 1",
            self.frontier_terrain,
            self.distance_rolls,
        )

        # Track signals for verification
        self.signals_received = []
        self._connect_signal_tracking()

    def _choose_army_by_id(self, army_unique_id: str):
        """Helper to choose an army by its unique ID."""
        all_players_data = self.engine.get_all_players_data()

        # Find the army across all players
        for _player_name, player_data in all_players_data.items():
            for army_type, army_data in player_data.get("armies", {}).items():
                if army_data.get("unique_id") == army_unique_id:
                    # Create the army data structure expected by choose_acting_army
                    army_choice_data = {
                        "name": army_data.get("name", f"{army_type.title()} Army"),
                        "army_type": army_type,
                        "location": army_data.get("location", "Unknown"),
                        "units": army_data.get("units", []),
                        "unique_id": army_data.get("unique_id", army_unique_id),
                    }
                    self.engine.choose_acting_army(army_choice_data)
                    return

        raise ValueError(f"Army with ID '{army_unique_id}' not found")

    def _connect_signal_tracking(self):
        """Connect to engine signals to track workflow progress."""
        self.engine.current_phase_changed.connect(
            lambda phase: self.signals_received.append(f"phase_changed: {phase}")
        )
        self.engine.terrain_direction_choice_requested.connect(
            lambda location, face: self.signals_received.append(
                f"terrain_direction_requested: {location}, face: {face}"
            )
        )

    def test_e2e_terrain_face_changes_with_maneuver(self):
        """
        E2E Test: Terrain face changes when maneuver succeeds

        Flow:
        1. Record initial terrain face
        2. Perform successful maneuver
        3. Choose terrain direction (UP or DOWN)
        4. Verify terrain face changed correctly
        """
        print("\n🧪 E2E Test: Terrain Face Changes with Maneuver")
        print("=" * 50)

        # Step 1: Record initial terrain state
        initial_terrains = self.engine.get_relevant_terrains_info()
        highland_initial = None
        for terrain in initial_terrains:
            if terrain["name"] == "Player 1 Highland":
                highland_initial = terrain["face"]
                break

        assert highland_initial is not None
        print(f"Initial Highland face: {highland_initial}")

        # Step 2: Player 1 maneuvers at home (where Player 2 horde is present)
        self._choose_army_by_id("player_1_home")
        self.engine.decide_maneuver(True)

        # Player 2 could counter but let's assume they decline
        self.engine.submit_counter_maneuver_decision("Player 2", False)

        # Step 3: Choose terrain direction UP (should increase face by 1)
        print("Step 3: Player 1 chooses to turn terrain UP")
        self.engine.submit_terrain_direction_choice("UP")

        # Step 4: Verify terrain face changed
        updated_terrains = self.engine.get_relevant_terrains_info()
        highland_final = None
        for terrain in updated_terrains:
            if terrain["name"] == "Player 1 Highland":
                highland_final = terrain["face"]
                break

        assert highland_final is not None
        print(f"Final Highland face: {highland_final}")

        # Face should have changed (UP typically means +1, wrapping at 8)
        expected_face = (highland_initial % 8) + 1 if highland_initial < 8 else 1
        assert highland_final == expected_face

        print("✅ Test completed - terrain face correctly updated")

    def test_e2e_terrain_face_changes_with_down_direction(self):
        """
        E2E Test: Terrain face changes when choosing DOWN direction

        Flow:
        1. Record initial terrain face
        2. Perform successful maneuver
        3. Choose terrain direction DOWN
        4. Verify terrain face decreased correctly
        """
        print("\n🧪 E2E Test: Terrain Face Changes with DOWN Direction")
        print("=" * 50)

        # Get frontier terrain initial face
        initial_terrains = self.engine.get_relevant_terrains_info()
        frontier_initial = None
        for terrain in initial_terrains:
            if terrain["name"] == "Coastland" and terrain["type"] == "Frontier":
                frontier_initial = terrain["face"]
                break

        assert frontier_initial is not None
        print(f"Initial Coastland face: {frontier_initial}")

        # Maneuver at frontier
        self._choose_army_by_id("player_1_campaign")
        self.engine.decide_maneuver(True)

        # No counter-maneuver (Player 2 horde is at Highland, not Coastland in this test)
        # Actually, let me check - Player 2 has home army at Coastland
        # Let's decline counter-maneuver
        self.engine.submit_counter_maneuver_decision("Player 2", False)

        # Choose DOWN direction
        print("Step 3: Player 1 chooses to turn terrain DOWN")
        self.engine.submit_terrain_direction_choice("DOWN")

        # Verify terrain face changed
        updated_terrains = self.engine.get_relevant_terrains_info()
        frontier_final = None
        for terrain in updated_terrains:
            if terrain["name"] == "Coastland" and terrain["type"] == "Frontier":
                frontier_final = terrain["face"]
                break

        assert frontier_final is not None
        print(f"Final Coastland face: {frontier_final}")

        # Face should have decreased (DOWN typically means -1, wrapping at 1)
        expected_face = (frontier_initial - 1) if frontier_initial > 1 else 8
        assert frontier_final == expected_face

        print("✅ Test completed - terrain face correctly decreased")

    def test_e2e_army_location_tracking_during_maneuvers(self):
        """
        E2E Test: Army locations are correctly tracked during complex maneuvers

        Flow:
        1. Verify initial army locations
        2. Perform maneuvers that might affect army positioning
        3. Verify army locations remain consistent
        """
        print("\n🧪 E2E Test: Army Location Tracking During Maneuvers")
        print("=" * 50)

        # Step 1: Verify initial army locations
        initial_state = self.engine.get_all_players_data()

        # Player 1 armies
        p1_home_location = initial_state["Player 1"]["armies"]["home"]["location"]
        p1_campaign_location = initial_state["Player 1"]["armies"]["campaign"][
            "location"
        ]

        # Player 2 armies
        p2_home_location = initial_state["Player 2"]["armies"]["home"]["location"]
        p2_horde_location = initial_state["Player 2"]["armies"]["horde"]["location"]

        print("Initial locations:")
        print(f"  P1 Home: {p1_home_location}")
        print(f"  P1 Campaign: {p1_campaign_location}")
        print(f"  P2 Home: {p2_home_location}")
        print(f"  P2 Horde: {p2_horde_location}")

        # Step 2: Perform maneuver at contested location
        self._choose_army_by_id("player_1_home")  # At Highland with P2 horde
        self.engine.decide_maneuver(True)
        self.engine.submit_counter_maneuver_decision("Player 2", True)
        self.engine.submit_maneuver_roll_results(5, 3)  # P1 wins
        self.engine.submit_terrain_direction_choice("UP")

        # Step 3: Verify army locations haven't changed inappropriately
        final_state = self.engine.get_all_players_data()

        # Locations should remain the same (maneuver affects terrain, not army positions)
        assert final_state["Player 1"]["armies"]["home"]["location"] == p1_home_location
        assert final_state["Player 1"]["armies"]["campaign"]["location"] == p1_campaign_location
        assert final_state["Player 2"]["armies"]["home"]["location"] == p2_home_location
        assert final_state["Player 2"]["armies"]["horde"]["location"] == p2_horde_location

        print("✅ Test completed - army locations correctly maintained")

    def test_e2e_multiple_terrains_different_faces(self):
        """
        E2E Test: Multiple terrains maintain different face values correctly

        Flow:
        1. Verify different terrains have different initial faces
        2. Perform actions that affect some but not all terrains
        3. Verify only affected terrains changed
        """
        print("\n🧪 E2E Test: Multiple Terrains with Different Faces")
        print("=" * 50)

        # Step 1: Record all initial terrain faces
        initial_terrains = self.engine.get_relevant_terrains_info()
        initial_faces = {}

        for terrain in initial_terrains:
            initial_faces[terrain["name"]] = terrain["face"]
            print(f"Initial {terrain['name']}: Face {terrain['face']}")

        # Should have at least 3 terrains
        assert len(initial_faces) >= 3

        # Step 2: Maneuver at Highland only
        self._choose_army_by_id("player_1_home")
        self.engine.decide_maneuver(True)
        self.engine.submit_counter_maneuver_decision(
            "Player 2", False
        )  # Decline counter
        self.engine.submit_terrain_direction_choice("UP")

        # Step 3: Verify only Highland changed
        final_terrains = self.engine.get_relevant_terrains_info()
        final_faces = {}

        for terrain in final_terrains:
            final_faces[terrain["name"]] = terrain["face"]
            print(f"Final {terrain['name']}: Face {terrain['face']}")

        # Highland should have changed
        highland_changed = False
        for name, face in final_faces.items():
            if "Highland" in name:
                if face != initial_faces[name]:
                    highland_changed = True
            else:
                # Other terrains should be unchanged
                assert face == initial_faces[name], f"Terrain {name} should not have changed"

        assert highland_changed, "Highland terrain face should have changed"

        print("✅ Test completed - selective terrain changes verified")

    def test_e2e_terrain_face_signal_includes_correct_data(self):
        """
        E2E Test: Terrain direction choice signal includes correct face information

        Flow:
        1. Trigger terrain direction choice
        2. Verify signal contains correct current face
        3. Verify face data matches engine state
        """
        print("\n🧪 E2E Test: Terrain Direction Signal Data Verification")
        print("=" * 50)

        # Clear previous signals
        self.signals_received.clear()

        # Get current Highland face
        current_terrains = self.engine.get_relevant_terrains_info()
        highland_face = None
        for terrain in current_terrains:
            if "Highland" in terrain["name"]:
                highland_face = terrain["face"]
                break

        assert highland_face is not None
        print(f"Current Highland face: {highland_face}")

        # Trigger terrain direction choice
        self._choose_army_by_id("player_1_home")
        self.engine.decide_maneuver(True)
        self.engine.submit_counter_maneuver_decision("Player 2", False)

        # Check that signal includes correct face information
        terrain_signals = [
            s for s in self.signals_received if "terrain_direction_requested" in s
        ]
        assert len(terrain_signals) == 1

        signal = terrain_signals[0]
        assert f"face: {highland_face}" in signal
        assert "Player 1 Highland" in signal

        print(f"Signal received: {signal}")
        print("✅ Test completed - terrain direction signal data verified")

    def test_e2e_army_unit_consistency_during_maneuvers(self):
        """
        E2E Test: Army unit compositions remain consistent during maneuvers

        Flow:
        1. Record initial unit compositions
        2. Perform various maneuvers
        3. Verify unit compositions unchanged (maneuvers don't affect units directly)
        """
        print("\n🧪 E2E Test: Army Unit Consistency During Maneuvers")
        print("=" * 50)

        # Step 1: Record initial unit counts
        initial_state = self.engine.get_all_players_data()
        initial_unit_counts = {}

        for player_name, player_data in initial_state.items():
            initial_unit_counts[player_name] = {}
            for army_type, army_data in player_data.get("armies", {}).items():
                unit_count = len(army_data.get("units", []))
                initial_unit_counts[player_name][army_type] = unit_count
                print(f"{player_name} {army_type}: {unit_count} units")

        # Step 2: Perform multiple maneuvers
        # First maneuver
        self._choose_army_by_id("player_1_home")
        self.engine.decide_maneuver(True)
        self.engine.submit_counter_maneuver_decision("Player 2", True)
        self.engine.submit_maneuver_roll_results(4, 2)
        self.engine.submit_terrain_direction_choice("UP")
        self.engine.select_action("SKIP")  # Complete the march

        # Advance to second march
        assert self.engine.current_phase == "SECOND_MARCH"

        # Second maneuver
        self._choose_army_by_id("player_1_campaign")
        self.engine.decide_maneuver(False)  # Skip maneuver
        self.engine.select_action("SKIP")  # Skip action

        # Complete reserves phase to advance to Player 2
        assert self.engine.current_phase == "RESERVES"
        self.engine.advance_phase()

        # Should advance to Player 2's turn
        assert self.engine.get_current_player_name() == "Player 2"

        # Step 3: Verify unit counts unchanged
        final_state = self.engine.get_all_players_data()

        for player_name, player_data in final_state.items():
            for army_type, army_data in player_data.get("armies", {}).items():
                final_unit_count = len(army_data.get("units", []))
                initial_count = initial_unit_counts[player_name][army_type]

                assert final_unit_count == initial_count, f"{player_name} {army_type} unit count changed from {initial_count} to {final_unit_count}"

                print(
                    f"{player_name} {army_type}: {final_unit_count} units (unchanged)"
                )

        print("✅ Test completed - unit compositions remained consistent")

    def tearDown(self):
        """Clean up after each test."""
        # Clear signals for next test
        self.signals_received.clear()


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
