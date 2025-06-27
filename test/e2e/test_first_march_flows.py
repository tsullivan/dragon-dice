#!/usr/bin/env python3
"""
End-to-end tests for First March phase flows.
These tests simulate complete user workflows to catch integration issues.
"""

import unittest
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from unittest.mock import patch, MagicMock

from game_logic.engine import GameEngine
from game_logic.game_state_manager import GameStateManager


class TestFirstMarchFlows(unittest.TestCase):
    """End-to-end tests for First March phase workflows."""

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
                        "location": "Coastland",  # Same frontier terrain as Player 1 campaign
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
        self.distance_rolls = [("Player 1", 3), ("Player 2", 5)]

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
        for player_name, player_data in all_players_data.items():
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
        self.engine.counter_maneuver_requested.connect(
            lambda location, armies: self.signals_received.append(
                f"counter_maneuver_requested: {location}"
            )
        )
        self.engine.simultaneous_maneuver_rolls_requested.connect(
            lambda player, army, opponents, responses: self.signals_received.append(
                "simultaneous_rolls_requested"
            )
        )
        self.engine.terrain_direction_choice_requested.connect(
            lambda location, face: self.signals_received.append(
                f"terrain_direction_requested: {location}"
            )
        )

    def test_e2e_maneuver_success_after_counter(self):
        """
        E2E Test: Player 1 First March - maneuver contested but player 1 wins

        Flow:
        1. Player 1 chooses acting army (campaign at Coastland)
        2. Player 1 decides to maneuver
        3. Player 2 counter-maneuvers
        4. Simultaneous rolls - Player 1 wins (3 vs 2)
        5. Player 1 chooses terrain direction
        6. Flow proceeds to action selection
        """
        print("\n🧪 E2E Test: Contested Maneuver - Player 1 Wins")
        print("=" * 50)

        # Step 1: Choose acting army
        print("Step 1: Player 1 chooses Campaign army at Coastland")
        self._choose_army_by_id("player_1_campaign")

        # Verify we're at maneuver decision step
        self.assertEqual(self.engine.current_march_step, "DECIDE_MANEUVER")

        # Step 2: Player 1 decides to maneuver
        print("Step 2: Player 1 decides to maneuver")
        self.engine.decide_maneuver(True)

        # Should trigger counter-maneuver request
        self.assertIn("counter_maneuver_requested: Coastland", self.signals_received)

        # Step 3: Player 2 decides to counter-maneuver
        print("Step 3: Player 2 chooses to counter-maneuver")
        self.engine.submit_counter_maneuver_decision("Player 2", True)

        # Should trigger simultaneous rolls request
        self.assertIn("simultaneous_rolls_requested", self.signals_received)

        # Step 4: Submit roll results - Player 1 wins
        print("Step 4: Simultaneous rolls - Player 1: 3, Player 2: 2")
        self.engine.submit_maneuver_roll_results(3, 2)  # Player 1 wins

        # Should request terrain direction choice
        self.assertIn("terrain_direction_requested: Coastland", self.signals_received)

        # Step 5: Player 1 chooses terrain direction
        print("Step 5: Player 1 chooses to turn terrain UP")
        self.engine.submit_terrain_direction_choice("UP")

        # Should advance to action selection
        self.assertEqual(self.engine.current_march_step, "SELECT_ACTION")

        print(
            "✅ Test completed successfully - maneuver succeeded and advanced to action selection"
        )

    def test_e2e_maneuver_failure_after_counter(self):
        """
        E2E Test: Player 1 First March - maneuver contested and player 1 loses

        Flow:
        1. Player 1 chooses acting army (campaign at Coastland)
        2. Player 1 decides to maneuver
        3. Player 2 counter-maneuvers
        4. Simultaneous rolls - Player 1 loses (2 vs 3)
        5. Flow should advance to action selection (no terrain direction choice)
        """
        print("\n🧪 E2E Test: Contested Maneuver - Player 1 Loses")
        print("=" * 50)

        # Step 1: Choose acting army
        print("Step 1: Player 1 chooses Campaign army at Coastland")
        self._choose_army_by_id("player_1_campaign")

        # Step 2: Player 1 decides to maneuver
        print("Step 2: Player 1 decides to maneuver")
        self.engine.decide_maneuver(True)

        # Step 3: Player 2 decides to counter-maneuver
        print("Step 3: Player 2 chooses to counter-maneuver")
        self.engine.submit_counter_maneuver_decision("Player 2", True)

        # Step 4: Submit roll results - Player 1 loses
        print("Step 4: Simultaneous rolls - Player 1: 2, Player 2: 3")
        self.engine.submit_maneuver_roll_results(2, 3)  # Player 1 loses

        # Should NOT request terrain direction choice (maneuver failed)
        terrain_direction_signals = [
            s for s in self.signals_received if "terrain_direction_requested" in s
        ]
        self.assertEqual(len(terrain_direction_signals), 0)

        # Should advance to action selection
        self.assertEqual(self.engine.current_march_step, "SELECT_ACTION")

        print(
            "✅ Test completed successfully - maneuver failed and advanced to action selection"
        )

    def test_e2e_no_maneuver_melee_action(self):
        """
        E2E Test: Player 1 First March - no maneuver, chooses melee action

        Flow:
        1. Player 1 chooses acting army (campaign at Coastland)
        2. Player 1 decides not to maneuver
        3. Flow advances to action selection
        4. Player 1 chooses melee action
        5. Flow advances to melee roll step
        """
        print("\n🧪 E2E Test: No Maneuver - Melee Action")
        print("=" * 50)

        # Step 1: Choose acting army
        print("Step 1: Player 1 chooses Campaign army at Coastland")
        self._choose_army_by_id("player_1_campaign")

        # Step 2: Player 1 decides not to maneuver
        print("Step 2: Player 1 decides not to maneuver")
        self.engine.decide_maneuver(False)

        # Should advance directly to action selection
        self.assertEqual(self.engine.current_march_step, "SELECT_ACTION")

        # Should NOT have any counter-maneuver requests
        counter_maneuver_signals = [
            s for s in self.signals_received if "counter_maneuver_requested" in s
        ]
        self.assertEqual(len(counter_maneuver_signals), 0)

        # Step 3: Player 1 chooses melee action
        print("Step 3: Player 1 chooses Melee Action")
        self.engine.select_action("MELEE")

        # Should advance to awaiting melee roll
        self.assertEqual(
            self.engine.current_action_step, "AWAITING_ATTACKER_MELEE_ROLL"
        )

        print(
            "✅ Test completed successfully - skipped maneuver and advanced to melee action"
        )

    def test_e2e_first_march_to_second_march(self):
        """
        E2E Test: Complete First March and advance to Second March

        Flow:
        1. Player 1 completes First March (no maneuver, skip action)
        2. Verify automatic advancement to Second March
        3. Verify it's still Player 1's turn
        """
        print("\n🧪 E2E Test: First March to Second March Progression")
        print("=" * 50)

        # Step 1: Choose acting army
        print("Step 1: Player 1 chooses Campaign army")
        self._choose_army_by_id("player_1_campaign")

        # Step 2: Skip maneuver
        print("Step 2: Player 1 skips maneuver")
        self.engine.decide_maneuver(False)

        # Step 3: Skip action
        print("Step 3: Player 1 skips action")
        self.engine.select_action("SKIP")

        # Should automatically advance to Second March
        self.assertEqual(self.engine.current_phase, "SECOND_MARCH")
        self.assertEqual(
            self.engine.get_current_player_name(), "Player 1"
        )  # Still Player 1's turn
        self.assertEqual(self.engine.current_march_step, "CHOOSE_ACTING_ARMY")

        print(
            "✅ Test completed successfully - advanced from First March to Second March"
        )

    def test_e2e_maneuver_automatic_success(self):
        """
        E2E Test: Player 1 maneuver with no opposition (automatic success)

        Flow:
        1. Player 1 chooses acting army at location with no opponents
        2. Player 1 decides to maneuver
        3. No counter-maneuver (automatic success)
        4. Player 1 chooses terrain direction
        5. Flow proceeds to action selection
        """
        print("\n🧪 E2E Test: Automatic Maneuver Success (No Opposition)")
        print("=" * 50)

        # Step 1: Choose acting army at home terrain (no opponents)
        print("Step 1: Player 1 chooses Home army at Player 1 Highland")
        self._choose_army_by_id("player_1_home")

        # Step 2: Player 1 decides to maneuver
        print("Step 2: Player 1 decides to maneuver")
        self.engine.decide_maneuver(True)

        # Should NOT trigger counter-maneuver request (no opponents)
        counter_maneuver_signals = [
            s for s in self.signals_received if "counter_maneuver_requested" in s
        ]
        self.assertEqual(len(counter_maneuver_signals), 0)

        # Should directly request terrain direction choice (automatic success)
        self.assertIn(
            "terrain_direction_requested: Player 1 Highland", self.signals_received
        )

        # Step 3: Player 1 chooses terrain direction
        print("Step 3: Player 1 chooses to turn terrain DOWN")
        self.engine.submit_terrain_direction_choice("DOWN")

        # Should advance to action selection
        self.assertEqual(self.engine.current_march_step, "SELECT_ACTION")

        print(
            "✅ Test completed successfully - automatic maneuver success with no opposition"
        )

    def tearDown(self):
        """Clean up after each test."""
        # Clear signals for next test
        self.signals_received.clear()


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
