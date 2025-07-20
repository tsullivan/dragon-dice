#!/usr/bin/env python3
"""
End-to-end tests for phase transitions and turn management.
Tests the broader game flow beyond individual march phases.
"""

import sys
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from game_logic.game_orchestrator import GameOrchestrator as GameEngine


class TestPhaseTransitions(unittest.TestCase):
    """End-to-end tests for phase transitions and turn management."""

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
                "force_size": 24,
                "selected_dragons": [],
                "armies": {
                    "home": {
                        "name": "Home Army",
                        "location": "Player 1 Highland",
                        "allocated_points": 10,
                        "units": [
                            {
                                "name": "Charioteer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "home_1",
                                "unit_type": "amazon_charioteer",
                            }
                        ],
                        "unique_id": "player_1_home",
                    },
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Coastland",
                        "allocated_points": 10,
                        "units": [
                            {
                                "name": "Soldier",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "campaign_1",
                                "unit_type": "amazon_soldier",
                            }
                        ],
                        "unique_id": "player_1_campaign",
                    },
                },
            },
            {
                "name": "Player 2",
                "home_terrain": "Coastland",
                "force_size": 24,
                "selected_dragons": [],
                "armies": {
                    "home": {
                        "name": "Home Army",
                        "location": "Player 2 Coastland",
                        "allocated_points": 10,
                        "units": [
                            {
                                "name": "Runner",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "home_p2_1",
                                "unit_type": "amazon_runner",
                            }
                        ],
                        "unique_id": "player_2_home",
                    },
                },
            },
        ]

        self.frontier_terrain = "Coastland"
        self.distance_rolls = [("Player 1", 3), ("Player 2", 5)]

        self.engine = GameEngine(
            self.player_setup_data,
            "Player 1",
            self.frontier_terrain,
            self.distance_rolls,
        )

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

    def test_e2e_complete_player_turn(self):
        """
        E2E Test: Complete Player 1's entire turn (First March + Second March)

        Flow:
        1. Player 1 First March: choose army, skip maneuver, skip action
        2. Player 1 Second March: choose army, skip maneuver, skip action
        3. Turn should advance to Player 2
        """
        print("\n🧪 E2E Test: Complete Player Turn")
        print("=" * 50)

        # Verify starting state
        assert self.engine.get_current_player_name() == "Player 1"
        assert self.engine.current_phase == "FIRST_MARCH"

        # === Player 1 First March ===
        print("=== Player 1 First March ===")

        # Choose acting army
        print("Step 1: Choose Campaign army")
        self._choose_army_by_id("player_1_campaign")

        # Skip maneuver
        print("Step 2: Skip maneuver")
        self.engine.decide_maneuver(False)

        # Skip action
        print("Step 3: Skip action")
        self.engine.select_action("SKIP")

        # Should advance to Second March
        assert self.engine.current_phase == "SECOND_MARCH"
        assert self.engine.get_current_player_name() == "Player 1"

        # === Player 1 Second March ===
        print("\n=== Player 1 Second March ===")

        # Choose acting army
        print("Step 4: Choose Home army")
        self._choose_army_by_id("player_1_home")

        # Skip maneuver
        print("Step 5: Skip maneuver")
        self.engine.decide_maneuver(False)

        # Skip action
        print("Step 6: Skip action")
        self.engine.select_action("SKIP")

        # Complete reserves phase to advance to Player 2
        assert self.engine.current_phase == "RESERVES"
        self.engine.advance_phase()

        # Should advance to Player 2's turn
        assert self.engine.get_current_player_name() == "Player 2"
        assert self.engine.current_phase == "FIRST_MARCH"

        print(
            "✅ Test completed successfully - Player 1 turn completed, advanced to Player 2"
        )

    def test_e2e_multi_player_turn_cycle(self):
        """
        E2E Test: Complete turn cycle for both players

        Flow:
        1. Player 1 completes both marches
        2. Player 2 completes both marches
        3. Should cycle back to Player 1 or advance to next phase
        """
        print("\n🧪 E2E Test: Multi-Player Turn Cycle")
        print("=" * 50)

        # Helper function to complete a player's turn quickly
        def complete_player_turn(player_name):
            print(f"\n--- Completing {player_name}'s turn ---")

            # First March
            assert self.engine.current_phase == "FIRST_MARCH"

            # Get available armies for this player
            all_players_data = self.engine.get_all_players_data()
            player_data = all_players_data.get(player_name, {})
            available_armies = []

            for army_type, army_data in player_data.get("armies", {}).items():
                army_info = {
                    "name": army_data.get("name", f"{army_type.title()} Army"),
                    "army_type": army_type,
                    "location": army_data.get("location", "Unknown"),
                    "units": army_data.get("units", []),
                    "unique_id": army_data.get(
                        "unique_id", f"{player_name}_{army_type}"
                    ),
                }
                available_armies.append(army_info)

            armies = available_armies
            assert len(armies) > 0, f"{player_name} should have available armies"

            # Choose first available army
            first_army_id = armies[0]["unique_id"]
            print(f"First March: Choose army {first_army_id}")
            self._choose_army_by_id(first_army_id)
            self.engine.decide_maneuver(False)
            self.engine.select_action("SKIP")

            # Second March
            assert self.engine.current_phase == "SECOND_MARCH"

            # Choose second available army if possible, otherwise same army
            # Get available armies again for second march
            all_players_data = self.engine.get_all_players_data()
            player_data = all_players_data.get(player_name, {})
            available_armies = []

            for army_type, army_data in player_data.get("armies", {}).items():
                army_info = {
                    "name": army_data.get("name", f"{army_type.title()} Army"),
                    "army_type": army_type,
                    "location": army_data.get("location", "Unknown"),
                    "units": army_data.get("units", []),
                    "unique_id": army_data.get(
                        "unique_id", f"{player_name}_{army_type}"
                    ),
                }
                available_armies.append(army_info)

            armies = available_armies
            second_army_id = (
                armies[1]["unique_id"] if len(armies) > 1 else armies[0]["unique_id"]
            )
            print(f"Second March: Choose army {second_army_id}")
            self._choose_army_by_id(second_army_id)
            self.engine.decide_maneuver(False)
            self.engine.select_action("SKIP")

            # Complete reserves phase to advance to next player
            assert self.engine.current_phase == "RESERVES"
            self.engine.advance_phase()

        # Complete Player 1's turn
        assert self.engine.get_current_player_name() == "Player 1"
        complete_player_turn("Player 1")

        # Should advance to Player 2
        assert self.engine.get_current_player_name() == "Player 2"
        complete_player_turn("Player 2")

        # After both players complete their turns, check state
        # (Could advance to next phase or cycle back depending on game rules)
        current_player = self.engine.get_current_player_name()
        current_phase = self.engine.current_phase

        print(f"After complete cycle: Player={current_player}, Phase={current_phase}")
        print("✅ Test completed successfully - multi-player turn cycle completed")

    def test_e2e_phase_skip_conditions(self):
        """
        E2E Test: Verify phase skip conditions work correctly

        Some phases might be skipped if no relevant actions are possible.
        """
        print("\n🧪 E2E Test: Phase Skip Conditions")
        print("=" * 50)

        # Start from the beginning
        initial_phase = self.engine.current_phase
        print(f"Initial phase: {initial_phase}")

        # The game should start in FIRST_MARCH, not in earlier phases that might be skipped
        # (like EXPIRE_EFFECTS, EIGHTH_FACE, etc. which might not apply on turn 1)
        assert initial_phase == "FIRST_MARCH"

        print("✅ Test completed successfully - phase skip conditions working")

    def test_e2e_game_state_consistency(self):
        """
        E2E Test: Verify game state remains consistent throughout transitions

        Flow:
        1. Perform various actions
        2. Verify terrain faces, army locations, and player data remain consistent
        """
        print("\n🧪 E2E Test: Game State Consistency")
        print("=" * 50)

        # Get initial state snapshot
        initial_terrains = self.engine.get_relevant_terrains_info()
        initial_armies = self.engine.get_available_acting_armies()

        print(f"Initial terrains: {len(initial_terrains)}")
        print(f"Initial armies: {len(initial_armies)}")

        # Perform some actions
        self._choose_army_by_id("player_1_campaign")
        self.engine.decide_maneuver(False)
        self.engine.select_action("SKIP")

        # Verify state consistency
        mid_terrains = self.engine.get_relevant_terrains_info()
        mid_armies = self.engine.get_available_acting_armies()

        # Terrain count should remain the same
        assert len(initial_terrains) == len(mid_terrains)

        # Army structure should remain consistent
        assert len(initial_armies) == len(mid_armies)

        print("✅ Test completed successfully - game state remains consistent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
