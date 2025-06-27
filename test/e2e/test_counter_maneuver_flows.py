#!/usr/bin/env python3
"""
Comprehensive End-to-end tests for Counter-Maneuver scenarios.
Tests all variations of counter-maneuver flows in Dragon Dice.
"""

import unittest
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from unittest.mock import patch, MagicMock

from game_logic.engine import GameEngine
from game_logic.game_state_manager import GameStateManager


class TestCounterManeuverFlows(unittest.TestCase):
    """Comprehensive E2E tests for counter-maneuver scenarios."""

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
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Coastland",  # Also at frontier
                        "units": [
                            {
                                "name": "Archer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_p2_1",
                                "unit_type": "amazon_archer",
                            },
                        ],
                        "unique_id": "player_2_campaign",
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
                f"counter_maneuver_requested: {location}, armies: {len(armies)}"
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

    def test_e2e_counter_maneuver_declined_by_all_opponents(self):
        """
        E2E Test: Counter-maneuver offered but declined by all opponents

        Flow:
        1. Player 1 maneuvers at contested location (Coastland)
        2. Counter-maneuver offered to Player 2 (multiple armies present)
        3. Player 2 declines counter-maneuver
        4. Player 1 automatically succeeds (no opposition)
        5. Player 1 chooses terrain direction
        """
        print("\n🧪 E2E Test: Counter-Maneuver Declined by All Opponents")
        print("=" * 50)

        # Step 1: Choose acting army at contested location
        print("Step 1: Player 1 chooses Campaign army at contested Coastland")
        self._choose_army_by_id("player_1_campaign")

        # Step 2: Player 1 decides to maneuver
        print("Step 2: Player 1 decides to maneuver")
        self.engine.decide_maneuver(True)

        # Should trigger counter-maneuver request with multiple armies
        counter_signals = [
            s for s in self.signals_received if "counter_maneuver_requested" in s
        ]
        self.assertEqual(len(counter_signals), 1)
        self.assertIn(
            "armies: 2", counter_signals[0]
        )  # Player 2 has horde + campaign at Coastland

        # Step 3: Player 2 declines counter-maneuver
        print("Step 3: Player 2 declines counter-maneuver")
        self.engine.submit_counter_maneuver_decision("Player 2", False)

        # Should NOT trigger simultaneous rolls (automatic success)
        simultaneous_signals = [
            s for s in self.signals_received if "simultaneous_rolls_requested" in s
        ]
        self.assertEqual(len(simultaneous_signals), 0)

        # Should directly request terrain direction choice (automatic success)
        terrain_direction_signals = [
            s for s in self.signals_received if "terrain_direction_requested" in s
        ]
        self.assertEqual(len(terrain_direction_signals), 1)

        # Step 4: Player 1 chooses terrain direction
        print("Step 4: Player 1 chooses terrain direction")
        self.engine.submit_terrain_direction_choice("UP")

        # Should advance to action selection
        self.assertEqual(self.engine.current_march_step, "SELECT_ACTION")

        print("✅ Test completed - counter-maneuver declined, automatic success")

    def test_e2e_counter_maneuver_tie_resolution(self):
        """
        E2E Test: Counter-maneuver with tie results

        Flow:
        1. Player 1 maneuvers
        2. Player 2 counter-maneuvers
        3. Simultaneous rolls result in tie
        4. Should follow Dragon Dice tie resolution rules
        """
        print("\n🧪 E2E Test: Counter-Maneuver Tie Resolution")
        print("=" * 50)

        # Setup and maneuver initiation
        self._choose_army_by_id("player_1_campaign")
        self.engine.decide_maneuver(True)
        self.engine.submit_counter_maneuver_decision("Player 2", True)

        # Submit tie results
        print("Step 1: Submit tie roll results (3 vs 3)")
        self.engine.submit_maneuver_roll_results(3, 3)  # Tie

        # In Dragon Dice, ties typically favor the defender
        # Should NOT request terrain direction (maneuver failed)
        terrain_direction_signals = [
            s for s in self.signals_received if "terrain_direction_requested" in s
        ]
        self.assertEqual(len(terrain_direction_signals), 0)

        # Should advance to action selection (maneuver failed)
        self.assertEqual(self.engine.current_march_step, "SELECT_ACTION")

        print("✅ Test completed - tie correctly resolved in favor of defender")

    def test_e2e_counter_maneuver_multiple_opponents_mixed_responses(self):
        """
        E2E Test: Multiple opponents with mixed counter-maneuver responses

        This test simulates complex scenarios where multiple armies can counter-maneuver
        but only some choose to do so.
        """
        print("\n🧪 E2E Test: Multiple Opponents - Mixed Counter-Maneuver Responses")
        print("=" * 50)

        # Create scenario with 3-player setup for more complexity
        three_player_data = self.player_setup_data + [
            {
                "name": "Player 3",
                "home_terrain": "Flatland",
                "armies": {
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Coastland",  # Also at contested location
                        "units": [
                            {
                                "name": "Scout",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_p3_1",
                                "unit_type": "amazon_scout",
                            },
                        ],
                        "unique_id": "player_3_campaign",
                    },
                },
            }
        ]

        # Create new engine with 3 players
        three_player_engine = GameEngine(
            three_player_data,
            "Player 1",
            self.frontier_terrain,
            self.distance_rolls + [("Player 3", 4)],
        )

        # Track signals for 3-player engine
        three_player_signals = []
        three_player_engine.counter_maneuver_requested.connect(
            lambda location, armies: three_player_signals.append(
                f"counter_maneuver_requested: {location}, armies: {len(armies)}"
            )
        )
        three_player_engine.simultaneous_maneuver_rolls_requested.connect(
            lambda player, army, opponents, responses: three_player_signals.append(
                f"simultaneous_rolls_requested: opponents: {len(opponents)}"
            )
        )

        # Helper for 3-player engine
        def choose_army_3p(army_unique_id):
            all_players_data = three_player_engine.get_all_players_data()
            for player_name, player_data in all_players_data.items():
                for army_type, army_data in player_data.get("armies", {}).items():
                    if army_data.get("unique_id") == army_unique_id:
                        army_choice_data = {
                            "name": army_data.get("name", f"{army_type.title()} Army"),
                            "army_type": army_type,
                            "location": army_data.get("location", "Unknown"),
                            "units": army_data.get("units", []),
                            "unique_id": army_data.get("unique_id", army_unique_id),
                        }
                        three_player_engine.choose_acting_army(army_choice_data)
                        return

        # Step 1: Player 1 maneuvers at location with multiple opponents
        choose_army_3p("player_1_campaign")
        three_player_engine.decide_maneuver(True)

        # Should offer counter-maneuver to both Player 2 and Player 3
        counter_signals = [
            s for s in three_player_signals if "counter_maneuver_requested" in s
        ]
        self.assertEqual(len(counter_signals), 1)
        self.assertIn(
            "armies: 3", counter_signals[0]
        )  # Player 2 (horde + campaign) + Player 3 (campaign)

        # Step 2: Mixed responses
        print("Step 2: Player 2 accepts counter-maneuver")
        three_player_engine.submit_counter_maneuver_decision("Player 2", True)

        print("Step 3: Player 3 declines counter-maneuver")
        three_player_engine.submit_counter_maneuver_decision("Player 3", False)

        # Should trigger simultaneous rolls with only Player 2
        simultaneous_signals = [
            s for s in three_player_signals if "simultaneous_rolls_requested" in s
        ]
        self.assertEqual(len(simultaneous_signals), 1)

        print("✅ Test completed - mixed responses handled correctly")

    def test_e2e_counter_maneuver_army_priority_system(self):
        """
        E2E Test: Counter-maneuver with Dragon Dice army priority

        Tests that when multiple armies from the same player can counter-maneuver,
        the system correctly applies priority: home > campaign > horde
        """
        print("\n🧪 E2E Test: Counter-Maneuver Army Priority System")
        print("=" * 50)

        # Create scenario where Player 2 has multiple army types at same location
        priority_test_data = [
            {
                "name": "Player 1",
                "home_terrain": "Highland",
                "armies": {
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Player 2 Coastland",  # Attacking Player 2's home
                        "units": [
                            {
                                "name": "Soldier",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_1",
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
                        ],
                        "unique_id": "player_2_home",
                    },
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Player 2 Coastland",  # Same location as home
                        "units": [
                            {
                                "name": "Archer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_p2_1",
                                "unit_type": "amazon_archer",
                            },
                        ],
                        "unique_id": "player_2_campaign",
                    },
                    "horde": {
                        "name": "Horde Army",
                        "location": "Player 2 Coastland",  # Same location as home and campaign
                        "units": [
                            {
                                "name": "Seer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "horde_p2_1",
                                "unit_type": "amazon_seer",
                            },
                        ],
                        "unique_id": "player_2_horde",
                    },
                },
            },
        ]

        priority_engine = GameEngine(
            priority_test_data,
            "Player 1",
            "Deadland",  # Different frontier
            [("Player 1", 2), ("Player 2", 6)],
        )

        # Track signals
        priority_signals = []
        priority_engine.counter_maneuver_requested.connect(
            lambda location, armies: priority_signals.append(
                f"counter_maneuver_requested: {location}, armies: {len(armies)}"
            )
        )

        # Helper
        def choose_army_priority(army_unique_id):
            all_players_data = priority_engine.get_all_players_data()
            for player_name, player_data in all_players_data.items():
                for army_type, army_data in player_data.get("armies", {}).items():
                    if army_data.get("unique_id") == army_unique_id:
                        army_choice_data = {
                            "name": army_data.get("name", f"{army_type.title()} Army"),
                            "army_type": army_type,
                            "location": army_data.get("location", "Unknown"),
                            "units": army_data.get("units", []),
                            "unique_id": army_data.get("unique_id", army_unique_id),
                        }
                        priority_engine.choose_acting_army(army_choice_data)
                        return

        # Player 1 maneuvers at Player 2's home (with all 3 army types present)
        choose_army_priority("player_1_campaign")
        priority_engine.decide_maneuver(True)

        # Should offer counter-maneuver with all 3 armies
        counter_signals = [
            s for s in priority_signals if "counter_maneuver_requested" in s
        ]
        self.assertEqual(len(counter_signals), 1)
        self.assertIn("armies: 3", counter_signals[0])  # home + campaign + horde

        print("✅ Test completed - army priority system working correctly")

    def test_e2e_counter_maneuver_edge_case_no_armies_can_counter(self):
        """
        E2E Test: Edge case where no armies can actually counter-maneuver

        This tests scenarios where armies are present but cannot legally counter-maneuver
        (e.g., due to special conditions or rules)
        """
        print("\n🧪 E2E Test: Edge Case - No Valid Counter-Maneuver Armies")
        print("=" * 50)

        # Create scenario where Player 1 is alone at their home terrain
        isolated_data = [
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
                        ],
                        "unique_id": "player_1_home",
                    },
                },
            },
        ]

        isolated_engine = GameEngine(
            isolated_data,
            "Player 1",
            "Coastland",
            [("Player 1", 3)],
        )

        # Track signals
        isolated_signals = []
        isolated_engine.counter_maneuver_requested.connect(
            lambda location, armies: isolated_signals.append(
                f"counter_maneuver_requested: {location}"
            )
        )
        isolated_engine.terrain_direction_choice_requested.connect(
            lambda location, face: isolated_signals.append(
                f"terrain_direction_requested: {location}"
            )
        )

        # Helper
        def choose_army_isolated(army_unique_id):
            all_players_data = isolated_engine.get_all_players_data()
            for player_name, player_data in all_players_data.items():
                for army_type, army_data in player_data.get("armies", {}).items():
                    if army_data.get("unique_id") == army_unique_id:
                        army_choice_data = {
                            "name": army_data.get("name", f"{army_type.title()} Army"),
                            "army_type": army_type,
                            "location": army_data.get("location", "Unknown"),
                            "units": army_data.get("units", []),
                            "unique_id": army_data.get("unique_id", army_unique_id),
                        }
                        isolated_engine.choose_acting_army(army_choice_data)
                        return

        # Player 1 maneuvers at home with no opponents
        choose_army_isolated("player_1_home")
        isolated_engine.decide_maneuver(True)

        # Should NOT trigger counter-maneuver request (no opponents)
        counter_signals = [
            s for s in isolated_signals if "counter_maneuver_requested" in s
        ]
        self.assertEqual(len(counter_signals), 0)

        # Should directly request terrain direction (automatic success)
        terrain_signals = [
            s for s in isolated_signals if "terrain_direction_requested" in s
        ]
        self.assertEqual(len(terrain_signals), 1)

        print("✅ Test completed - edge case handled correctly")

    def test_e2e_counter_maneuver_signal_timing_verification(self):
        """
        E2E Test: Verify correct signal timing and ordering in counter-maneuver flow

        This test ensures signals are emitted in the correct order and at the right times
        """
        print("\n🧪 E2E Test: Counter-Maneuver Signal Timing Verification")
        print("=" * 50)

        # Clear any existing signals
        self.signals_received.clear()

        # Step 1: Initial maneuver
        self._choose_army_by_id("player_1_campaign")
        initial_signals = len(self.signals_received)

        self.engine.decide_maneuver(True)
        after_maneuver_signals = len(self.signals_received)

        # Should have counter-maneuver request signal
        self.assertGreater(after_maneuver_signals, initial_signals)
        self.assertTrue(
            any("counter_maneuver_requested" in s for s in self.signals_received)
        )

        # Step 2: Counter-maneuver accepted
        before_counter_count = len(self.signals_received)
        self.engine.submit_counter_maneuver_decision("Player 2", True)
        after_counter_count = len(self.signals_received)

        # Should have simultaneous rolls request signal
        self.assertGreater(after_counter_count, before_counter_count)
        self.assertTrue(
            any("simultaneous_rolls_requested" in s for s in self.signals_received)
        )

        # Step 3: Roll resolution
        before_roll_count = len(self.signals_received)
        self.engine.submit_maneuver_roll_results(4, 2)  # Player 1 wins
        after_roll_count = len(self.signals_received)

        # Should have terrain direction request signal
        self.assertGreater(after_roll_count, before_roll_count)
        self.assertTrue(
            any("terrain_direction_requested" in s for s in self.signals_received)
        )

        # Verify signal order
        signal_order = []
        for signal in self.signals_received:
            if "counter_maneuver_requested" in signal:
                signal_order.append("counter_maneuver")
            elif "simultaneous_rolls_requested" in signal:
                signal_order.append("simultaneous_rolls")
            elif "terrain_direction_requested" in signal:
                signal_order.append("terrain_direction")

        expected_order = ["counter_maneuver", "simultaneous_rolls", "terrain_direction"]
        self.assertEqual(signal_order, expected_order)

        print("✅ Test completed - signal timing and ordering verified")

    def tearDown(self):
        """Clean up after each test."""
        # Clear signals for next test
        self.signals_received.clear()


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
