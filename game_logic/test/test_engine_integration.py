import unittest
from unittest.mock import MagicMock, Mock, patch

import constants
from game_logic.game_orchestrator import GameOrchestrator as GameEngine
from models.test.mock import create_army_dict, create_player_setup_dict


class TestEngineIntegration(unittest.TestCase):
    """Test Engine integration and critical game flow logic."""

    def setUp(self):
        """Set up test data for engine integration tests using type-safe mocks."""
        # Create Player 1 with complete mock data
        player1_data = create_player_setup_dict(name="Player 1", home_terrain="Highland", force_size=24)
        player1_data["armies"] = {
            "home": create_army_dict(
                name="Home Army",
                location="Player 1 Highland",
                allocated_points=10,
                unique_id="player_1_home",
                unit_count=1,
            ),
            "campaign": create_army_dict(
                name="Campaign Army",
                location="Swampland (Green, Yellow)",
                allocated_points=10,
                unique_id="player_1_campaign",
                unit_count=1,
            ),
        }

        # Create Player 2 with complete mock data
        player2_data = create_player_setup_dict(name="Player 2", home_terrain="Coastland", force_size=24)
        player2_data["armies"] = {
            "home": create_army_dict(
                name="Home Army",
                location="Player 2 Coastland",
                allocated_points=10,
                unique_id="player_2_home",
                unit_count=1,
            ),
            "horde": create_army_dict(
                name="Horde Army",
                location="Player 1 Highland",  # At Player 1's home
                allocated_points=10,
                unique_id="player_2_horde",
                unit_count=1,
            ),
        }

        self.player_setup_data = [player1_data, player2_data]

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
        assert self.engine.player_names == ["Player 1", "Player 2"]
        assert self.engine.first_player_name == "Player 1"
        assert self.engine.frontier_terrain == self.frontier_terrain
        assert self.engine.distance_rolls == self.distance_rolls

        # Check that managers are properly initialized
        assert self.engine.turn_manager is not None
        assert self.engine.effect_manager is not None
        assert self.engine.game_state_manager is not None
        assert self.engine.action_resolver is not None

    def test_current_player_tracking(self):
        """Test current player tracking."""
        current_player = self.engine.get_current_player_name()
        assert current_player == "Player 1"  # First player

    def test_acting_army_selection(self):
        """Test acting army selection and tracking."""
        test_army = {
            "name": "Test Army",
            "location": "Test Location",
            "unique_id": "test_army_id",
        }

        self.engine.choose_acting_army(test_army)

        current_acting_army = self.engine.get_current_acting_army()
        assert current_acting_army == test_army
        assert current_acting_army["name"] == "Test Army"

    def test_action_selection(self):
        """Test action selection and state transitions."""
        # Test melee action selection
        self.engine.select_action("MELEE")
        assert self.engine.current_action_step == "AWAITING_ATTACKER_MELEE_ROLL"

        # Test missile action selection
        self.engine.select_action("MISSILE")
        assert self.engine.current_action_step == "AWAITING_ATTACKER_MISSILE_ROLL"

        # Test magic action selection
        self.engine.select_action("MAGIC")
        assert self.engine.current_action_step == "AWAITING_MAGIC_ROLL"

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

            assert success
            mock_update.assert_called_once_with("Player 1 Highland", "3")

    def test_maneuver_results_application_failure(self):
        """Test handling of failed maneuver results."""
        maneuver_result = {"success": False, "location": "Player 1 Highland"}

        # Should not attempt to update terrain for failed maneuver
        with patch.object(self.engine.game_state_manager, "update_terrain_face") as mock_update:
            result = self.engine.apply_maneuver_results(maneuver_result)

            assert result is None
            mock_update.assert_not_called()

    def test_phase_management(self):
        """Test phase management and transitions."""
        # Test initial phase
        assert self.engine.current_phase is not None

        # Test phase advancement
        with patch.object(self.engine, "phase_advance_requested") as mock_signal:
            self.engine.advance_phase()
            mock_signal.emit.assert_called_once()

    def test_march_step_management(self):
        """Test march step management."""
        # Test march step transitions
        self.engine._current_march_step = "CHOOSE_ACTING_ARMY"
        assert self.engine.current_march_step == "CHOOSE_ACTING_ARMY"

    def test_get_current_phase_display(self):
        """Test phase display formatting."""
        # Test very first turn display
        self.engine._current_phase = "FIRST_MARCH"
        self.engine._is_very_first_turn = True
        self.engine._current_march_step = "DECIDE_MANEUVER"

        display = self.engine.get_current_phase_display()
        assert "Game Start" in display

        # Test normal phase display
        self.engine._is_very_first_turn = False
        self.engine._current_phase = "EIGHTH_FACE"
        self.engine._current_march_step = ""

        display = self.engine.get_current_phase_display()
        assert "Eighth Face" in display

    def test_data_retrieval_methods(self):
        """Test data retrieval methods."""
        # Test player data retrieval
        all_players = self.engine.get_all_players_data()
        assert isinstance(all_players, dict)
        assert "Player 1" in all_players
        assert "Player 2" in all_players

        # Test terrain data retrieval
        terrain_data = self.engine.get_all_terrain_data()
        assert isinstance(terrain_data, dict)

        # Test terrain type extraction
        terrain_type = self.engine.extract_terrain_type_from_location("Player 1 Highland")
        assert terrain_type == "Highland"

    def test_error_handling_in_action_flow(self):
        """Test error handling in action flow."""
        # Test with invalid action type
        self.engine.select_action("INVALID_ACTION")

        # Should not crash - engine should handle gracefully
        assert self.engine.current_action_step is not None


if __name__ == "__main__":
    unittest.main()
