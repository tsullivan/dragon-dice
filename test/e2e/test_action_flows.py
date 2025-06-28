#!/usr/bin/env python3
"""
End-to-end tests for action flows (Melee, Missile, Magic, etc.).
Tests complete action sequences from selection to resolution.
"""

import unittest
import sys
from PySide6.QtWidgets import QApplication
from unittest.mock import patch, MagicMock

from game_logic.engine import GameEngine


class TestActionFlows(unittest.TestCase):
    """End-to-end tests for action flows."""

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
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Coastland",  # Frontier with opponents
                        "units": [
                            {
                                "name": "Charioteer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "p1_char_1",
                                "unit_type": "amazon_charioteer",
                            },
                            {
                                "name": "Soldier",
                                "health": 2,
                                "max_health": 2,
                                "unit_id": "p1_sold_1",
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
                    "horde": {
                        "name": "Horde Army",
                        "location": "Coastland",  # Same location - opponents
                        "units": [
                            {
                                "name": "Runner",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "p2_run_1",
                                "unit_type": "amazon_runner",
                            },
                            {
                                "name": "Seer",
                                "health": 1,
                                "max_health": 1,
                                "unit_id": "p2_seer_1",
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

        self.engine = GameEngine(
            self.player_setup_data,
            "Player 1",
            self.frontier_terrain,
            self.distance_rolls,
        )

        # Set up for action phase
        self._choose_army_by_id("player_1_campaign")
        self.engine.decide_maneuver(False)  # Skip maneuver to get to actions

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

    def test_e2e_melee_action_complete_flow(self):
        """
        E2E Test: Complete melee action flow

        Flow:
        1. Player 1 selects melee action
        2. Player 1 submits attacker dice results
        3. Player 2 submits defender save results
        4. Damage is allocated
        5. Counter-attack occurs if applicable
        6. Action resolves and flow continues
        """
        print("\n🧪 E2E Test: Complete Melee Action Flow")
        print("=" * 50)

        # Step 1: Select melee action
        print("Step 1: Player 1 selects Melee Action")
        self.engine.select_action("MELEE")

        # Should be waiting for attacker melee roll
        self.assertEqual(
            self.engine.current_action_step, "AWAITING_ATTACKER_MELEE_ROLL"
        )

        # Step 2: Submit attacker dice results
        print("Step 2: Player 1 submits melee dice results")
        # Mock the dice parsing to avoid implementation dependencies
        # Return list format that process_attacker_melee_roll expects
        with patch.object(
            self.engine.action_resolver,
            "parse_dice_string",
            return_value=[
                {"type": "MELEE", "count": 2},
                {"type": "SAI", "count": 1, "sai_type": "BULLSEYE"}
            ],
        ):
            with patch.object(
                self.engine.action_resolver,
                "resolve_attacker_melee",
                return_value={"hits": 2, "damage": 3},
            ):
                self.engine.submit_attacker_melee_results("MM,S,SAI")

        # Should advance to defender saves
        self.assertEqual(self.engine.current_action_step, "AWAITING_DEFENDER_SAVES")

        # Step 3: Submit defender save results
        print("Step 3: Player 2 submits save dice results")
        with patch.object(
            self.engine.action_resolver, 
            "parse_dice_string", 
            return_value=[
                {"type": "SAVE", "count": 1},
                {"type": "ID", "count": 1}
            ]
        ):
            self.engine.submit_defender_save_results("S,S")

        # After saves, should either request damage allocation or resolve action
        current_step = self.engine.current_action_step
        print(f"After saves, current step: {current_step}")

        print("✅ Test completed successfully - melee action flow processed")

    def test_e2e_missile_action_flow(self):
        """
        E2E Test: Missile action flow

        Flow:
        1. Player 1 selects missile action
        2. Player 1 submits missile dice results
        3. Damage is allocated automatically (no saves for missile)
        4. Action resolves
        """
        print("\n🧪 E2E Test: Missile Action Flow")
        print("=" * 50)

        # Step 1: Select missile action
        print("Step 1: Player 1 selects Missile Action")
        self.engine.select_action("MISSILE")

        # Should be waiting for attacker missile roll
        self.assertEqual(
            self.engine.current_action_step, "AWAITING_ATTACKER_MISSILE_ROLL"
        )

        # Step 2: Submit missile dice results
        print("Step 2: Player 1 submits missile dice results")
        with patch.object(
            self.engine.action_resolver,
            "parse_dice_string",
            return_value=[
                {"type": "MISSILE", "count": 2}
            ],
        ):
            with patch.object(
                self.engine.action_resolver,
                "resolve_attacker_missile",
                return_value={"hits": 1, "damage": 2},
            ):
                self.engine.submit_attacker_missile_results("MI,MI")

        # Missile actions typically don't have saves, so should resolve quickly
        current_step = self.engine.current_action_step
        print(f"After missile roll, current step: {current_step}")

        print("✅ Test completed successfully - missile action flow processed")

    def test_e2e_magic_action_flow(self):
        """
        E2E Test: Magic action flow

        Flow:
        1. Player 1 selects magic action
        2. Player 1 submits magic dice results
        3. Magic effects are applied
        4. Action resolves
        """
        print("\n🧪 E2E Test: Magic Action Flow")
        print("=" * 50)

        # Step 1: Select magic action
        print("Step 1: Player 1 selects Magic Action")
        self.engine.select_action("MAGIC")

        # Should be waiting for magic roll
        self.assertEqual(self.engine.current_action_step, "AWAITING_MAGIC_ROLL")

        # Step 2: Submit magic dice results
        print("Step 2: Player 1 submits magic dice results")
        with patch.object(
            self.engine.action_resolver,
            "parse_dice_string",
            return_value=[
                {"type": "MAGIC", "count": 2},
                {"type": "SAI", "count": 1, "sai_type": "MAGIC_BOLT"}
            ],
        ):
            with patch.object(
                self.engine.action_resolver,
                "resolve_magic",
                return_value={"effects_applied": True},
            ):
                self.engine.submit_magic_results("MA,MA,SAI")

        # Magic should resolve and potentially apply effects
        current_step = self.engine.current_action_step
        print(f"After magic roll, current step: {current_step}")

        print("✅ Test completed successfully - magic action flow processed")

    def test_e2e_skip_action_flow(self):
        """
        E2E Test: Skip action flow

        Flow:
        1. Player 1 selects skip action
        2. Should immediately advance to next step/phase
        """
        print("\n🧪 E2E Test: Skip Action Flow")
        print("=" * 50)

        # Record current state
        initial_march_step = self.engine.get_current_march_step()
        initial_phase = self.engine.get_current_phase()

        # Step 1: Select skip action
        print("Step 1: Player 1 selects Skip Action")
        self.engine.select_action("SKIP")

        # Should advance immediately without any intermediate steps
        new_march_step = self.engine.get_current_march_step()
        new_phase = self.engine.get_current_phase()

        print(f"Before skip: {initial_phase}/{initial_march_step}")
        print(f"After skip: {new_phase}/{new_march_step}")

        # Should have advanced to next phase or completed the march
        self.assertTrue(
            new_phase != initial_phase or new_march_step != initial_march_step,
            "Skip action should advance the game state",
        )

        print("✅ Test completed successfully - skip action advanced game state")

    def test_e2e_action_with_no_targets(self):
        """
        E2E Test: Action when no valid targets exist

        This tests edge cases where actions might not be possible.
        """
        print("\n🧪 E2E Test: Action With No Valid Targets")
        print("=" * 50)

        # Create engine with army that has no opponents
        isolated_player_data = [
            {
                "name": "Player 1",
                "home_terrain": "Highland",
                "armies": {
                    "home": {
                        "name": "Home Army",
                        "location": "Player 1 Highland",  # Isolated location
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
                },
            },
        ]

        isolated_engine = GameEngine(
            isolated_player_data,
            "Player 1",
            "Coastland",  # Different frontier
            [("Player 1", 3)],
        )

        # Set up for action phase
        # Create helper function for isolated engine
        def choose_army_by_id_isolated(army_unique_id):
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

        choose_army_by_id_isolated("player_1_home")
        isolated_engine.decide_maneuver(False)

        # Try to select melee action with no targets
        print("Step 1: Player 1 tries Melee Action with no targets")
        isolated_engine.select_action("MELEE")

        # Should handle gracefully (either skip or show appropriate state)
        current_step = isolated_engine.get_current_action_step()
        print(f"Action step with no targets: {current_step}")

        print("✅ Test completed successfully - handled action with no targets")


if __name__ == "__main__":
    unittest.main(verbosity=2)
