import unittest
from unittest.mock import MagicMock, Mock, patch

import constants
from game_logic.engine import GameEngine


class TestEngineIntegration(unittest.TestCase):
    """Test Engine integration and critical game flow logic."""

    def setUp(self):
        """Set up test data for engine integration tests."""
        self.player_setup_data = [
            {
                "name": "Player 1",
                "home_terrain": "Highland",
                "armies": {
                    "home": {
                        "name": "Home Army",
                        "location": "Player 1 Highland",
                        "units": [{"name": "Test Unit", "health": 2}],
                        "unique_id": "player_1_home",
                    },
                    "campaign": {
                        "name": "Campaign Army",
                        "location": "Swampland (Green, Yellow)",
                        "units": [{"name": "Test Unit", "health": 2}],
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
                        "units": [{"name": "Test Unit", "health": 2}],
                        "unique_id": "player_2_home",
                    },
                    "horde": {
                        "name": "Horde Army",
                        "location": "Player 1 Highland",  # At Player 1's home
                        "units": [{"name": "Test Unit", "health": 2}],
                        "unique_id": "player_2_horde",
                    },
                },
            },
        ]

        self.frontier_terrain = "Swampland (Green, Yellow)"
        self.distance_rolls = [("Player 1", 5), ("Player 2", 3)]

        self.engine = GameEngine(
            self.player_setup_data,
            "Player 1",
            self.frontier_terrain,
            self.distance_rolls,
        )

    def test_engine_initialization(self):
        """Test proper engine initialization."""
        self.assertEqual(self.engine.player_names, ["Player 1", "Player 2"])
        self.assertEqual(self.engine.first_player_name, "Player 1")
        self.assertEqual(self.engine.frontier_terrain, self.frontier_terrain)
        self.assertEqual(self.engine.distance_rolls, self.distance_rolls)

        # Check that managers are properly initialized
        self.assertIsNotNone(self.engine.turn_manager)
        self.assertIsNotNone(self.engine.effect_manager)
        self.assertIsNotNone(self.engine.game_state_manager)
        self.assertIsNotNone(self.engine.action_resolver)

    def test_current_player_tracking(self):
        """Test current player tracking."""
        current_player = self.engine.get_current_player_name()
        self.assertEqual(current_player, "Player 1")  # First player

    def test_acting_army_selection(self):
        """Test acting army selection and tracking."""
        test_army = {
            "name": "Test Army",
            "location": "Test Location",
            "unique_id": "test_army_id",
        }

        self.engine.choose_acting_army(test_army)

        current_acting_army = self.engine.get_current_acting_army()
        self.assertEqual(current_acting_army, test_army)
        self.assertEqual(current_acting_army["name"], "Test Army")

    def test_action_selection(self):
        """Test action selection and state transitions."""
        # Test melee action selection
        self.engine.select_action("MELEE")
        self.assertEqual(
            self.engine.current_action_step,
            "AWAITING_ATTACKER_MELEE_ROLL",
        )

        # Test missile action selection
        self.engine.select_action("MISSILE")
        self.assertEqual(
            self.engine.current_action_step,
            "AWAITING_ATTACKER_MISSILE_ROLL",
        )

        # Test magic action selection
        self.engine.select_action("MAGIC")
        self.assertEqual(self.engine.current_action_step, "AWAITING_MAGIC_ROLL")

    def test_submit_defender_save_results_no_pending_outcome(self):
        """Test defender save submission without pending attacker outcome."""
        # No pending outcome
        self.engine.pending_attacker_outcome = None

        with patch.object(self.engine.action_resolver, "parse_dice_string") as mock_parse:
            mock_parse.return_value = {"saves": 1}

            # Should handle gracefully and not crash
            self.engine.submit_defender_save_results("S")

    def test_maneuver_results_application(self):
        """Test application of maneuver results."""
        maneuver_result = {
            "success": True,
            "location": "Player 1 Highland",
            "old_face": 2,
            "new_face": 3,
            "direction": "UP",
            "maneuver_icons": 1,
        }

        with patch.object(self.engine.game_state_manager, "update_terrain_face") as mock_update:
            mock_update.return_value = True

            success = self.engine.apply_maneuver_results(maneuver_result)

            self.assertTrue(success)
            mock_update.assert_called_once_with("Player 1 Highland", "3")

    def test_maneuver_results_application_failure(self):
        """Test handling of failed maneuver results."""
        maneuver_result = {"success": False, "location": "Player 1 Highland"}

        # Should not attempt to update terrain for failed maneuver
        with patch.object(self.engine.game_state_manager, "update_terrain_face") as mock_update:
            result = self.engine.apply_maneuver_results(maneuver_result)

            self.assertIsNone(result)
            mock_update.assert_not_called()

    def test_phase_management(self):
        """Test phase management and transitions."""
        # Test initial phase
        self.assertIsNotNone(self.engine.current_phase)

        # Test phase advancement
        with patch.object(self.engine, "phase_advance_requested") as mock_signal:
            self.engine.advance_phase()
            mock_signal.emit.assert_called_once()

    def test_march_step_management(self):
        """Test march step management."""
        # Test march step transitions
        self.engine._current_march_step = "CHOOSE_ACTING_ARMY"
        self.assertEqual(self.engine.current_march_step, "CHOOSE_ACTING_ARMY")

    def test_get_current_phase_display(self):
        """Test phase display formatting."""
        # Test very first turn display
        self.engine._current_phase = "FIRST_MARCH"
        self.engine._is_very_first_turn = True
        self.engine._current_march_step = "DECIDE_MANEUVER"

        display = self.engine.get_current_phase_display()
        self.assertIn("Game Start", display)

        # Test normal phase display
        self.engine._is_very_first_turn = False
        self.engine._current_phase = "EIGHTH_FACE"
        self.engine._current_march_step = ""

        display = self.engine.get_current_phase_display()
        self.assertIn("Eighth Face", display)

    def test_data_retrieval_methods(self):
        """Test data retrieval methods."""
        # Test player data retrieval
        all_players = self.engine.get_all_players_data()
        self.assertIsInstance(all_players, dict)
        self.assertIn("Player 1", all_players)
        self.assertIn("Player 2", all_players)

        # Test terrain data retrieval
        terrain_data = self.engine.get_all_terrain_data()
        self.assertIsInstance(terrain_data, dict)

        # Test terrain type extraction
        terrain_type = self.engine.extract_terrain_type_from_location("Player 1 Highland")
        self.assertEqual(terrain_type, "Highland")

    def test_error_handling_in_action_flow(self):
        """Test error handling in action flow."""
        # Test with invalid action type
        self.engine.select_action("INVALID_ACTION")

        # Should not crash - engine should handle gracefully
        self.assertIsNotNone(self.engine.current_action_step)


if __name__ == "__main__":
    unittest.main()
