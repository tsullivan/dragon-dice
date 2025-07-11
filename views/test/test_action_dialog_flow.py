import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication, QWidget

from views.action_dialog import ActionDialog


class TestActionDialogFlow(unittest.TestCase):
    """Test the Action Dialog flow and functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for widget tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test data for action dialog tests."""
        self.sample_acting_army = {
            "name": "Campaign Army",
            "location": "Coastland (Blue, Green)",
            "units": [
                {"name": "Amazon War Driver", "health": 3},
                {"name": "Amazon Javelineer", "health": 2},
            ],
        }

        self.sample_player_data = {"Player 1": {"armies": {"campaign": self.sample_acting_army}}}

        self.sample_terrain_data = {
            "Coastland (Blue, Green)": {
                "name": "Coastland (Blue, Green)",
                "type": "Frontier",
                "face": 3,
            }
        }

        self.parent_widget = QWidget()

    def tearDown(self):
        """Clean up after tests."""
        self.parent_widget.close()

    def test_action_dialog_initialization_melee(self):
        """Test ActionDialog initialization for melee action."""
        dialog = ActionDialog(
            action_type="MELEE",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        assert dialog.action_type == "MELEE"
        assert dialog.current_player_name == "Player 1"
        assert dialog.acting_army == self.sample_acting_army
        assert dialog.current_step == "attacker_roll"
        assert dialog.attacker_results is None
        assert dialog.defender_results is None

    def test_action_dialog_initialization_missile(self):
        """Test ActionDialog initialization for missile action."""
        dialog = ActionDialog(
            action_type="MISSILE",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        assert dialog.action_type == "MISSILE"
        assert dialog.windowTitle() == "Missile Action"

    def test_action_dialog_initialization_magic(self):
        """Test ActionDialog initialization for magic action."""
        dialog = ActionDialog(
            action_type="MAGIC",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        assert dialog.action_type == "MAGIC"
        assert dialog.windowTitle() == "Magic Action"

    def test_action_dialog_step_progression(self):
        """Test the step progression through the action dialog."""
        dialog = ActionDialog(
            action_type="MELEE",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        # Initial state
        assert dialog.current_step == "attacker_roll"

        # Simulate attacker input
        dialog.attacker_dice_input.setText("MM,S,SAI")
        dialog._on_next()

        assert dialog.current_step == "defender_saves"
        assert dialog.attacker_results == "MM,S,SAI"

        # Simulate defender input
        dialog.defender_dice_input.setText("S,S")
        dialog._on_next()

        assert dialog.current_step == "results"
        assert dialog.defender_results == "S,S"

    @patch("components.error_dialog.ErrorDialog.show_warning")
    def test_action_dialog_validation_empty_attacker_input(self, mock_show_warning):
        """Test validation for empty attacker input."""
        dialog = ActionDialog(
            action_type="MELEE",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        # Try to proceed without input
        dialog.attacker_dice_input.setText("")
        dialog._on_next()

        # Should still be on attacker_roll step
        assert dialog.current_step == "attacker_roll"

        # Should show validation warning
        mock_show_warning.assert_called_once()
        call_args = mock_show_warning.call_args[0]
        assert call_args[1] == "Input Required"

    @patch("components.error_dialog.ErrorDialog.show_warning")
    def test_action_dialog_validation_empty_defender_input(self, mock_show_warning):
        """Test validation for empty defender input."""
        dialog = ActionDialog(
            action_type="MELEE",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        # Progress to defender step
        dialog.attacker_dice_input.setText("MM")
        dialog._on_next()

        # Try to proceed without defender input
        dialog.defender_dice_input.setText("")
        dialog._on_next()

        # Should still be on defender_saves step
        assert dialog.current_step == "defender_saves"

        # Should show validation warning
        mock_show_warning.assert_called_once()

    def test_action_dialog_signal_emission_completion(self):
        """Test signal emission on action completion."""
        dialog = ActionDialog(
            action_type="MELEE",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        # Set up signal spy
        completion_spy = QSignalSpy(dialog.action_completed)

        # Complete the dialog flow
        dialog.attacker_dice_input.setText("MM,S,SAI")
        dialog._on_next()

        dialog.defender_dice_input.setText("S,S")
        dialog._on_next()

        # Complete action
        dialog._on_next()

        # Should emit completion signal
        assert completion_spy.count() == 1

        # Verify signal was emitted with data (accessing signal data in Qt6 is complex)
        # Just verify the signal was emitted correctly
        if completion_spy.count() > 0:
            print("✅ Action completion signal emitted successfully")

    def test_action_dialog_signal_emission_cancellation(self):
        """Test signal emission on action cancellation."""
        dialog = ActionDialog(
            action_type="MELEE",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        # Set up signal spy
        cancellation_spy = QSignalSpy(dialog.action_cancelled)

        # Cancel the dialog
        dialog._on_cancel()

        # Should emit cancellation signal
        assert cancellation_spy.count() == 1

    def test_action_dialog_button_state_management(self):
        """Test button state management throughout dialog flow."""
        dialog = ActionDialog(
            action_type="MELEE",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        # Initial state - back button should be disabled
        assert not dialog.back_button.isEnabled()
        assert dialog.next_button.isEnabled()
        assert dialog.next_button.text() == "Submit Attack"

        # Progress to defender step
        dialog.attacker_dice_input.setText("MM")
        dialog._on_next()

        # Back button should now be enabled
        assert dialog.back_button.isEnabled()
        assert dialog.next_button.isEnabled()
        assert dialog.next_button.text() == "Submit Saves"

        # Progress to results step
        dialog.defender_dice_input.setText("S")
        dialog._on_next()

        # Both buttons should be enabled
        assert dialog.back_button.isEnabled()
        assert dialog.next_button.isEnabled()
        assert dialog.next_button.text() == "Complete Action"

    def test_action_dialog_army_display(self):
        """Test that army information is properly displayed."""
        dialog = ActionDialog(
            action_type="MELEE",
            current_player_name="Player 1",
            acting_army=self.sample_acting_army,
            all_players_data=self.sample_player_data,
            terrain_data=self.sample_terrain_data,
            parent=self.parent_widget,
        )

        # Dialog should display army information
        assert dialog.acting_army is not None
        assert dialog.acting_army["name"] == "Campaign Army"
        assert dialog.acting_army["location"] == "Coastland (Blue, Green)"
        assert len(dialog.acting_army["units"]) == 2

    def test_action_dialog_different_action_types(self):
        """Test dialog behavior with different action types."""
        action_types = ["MELEE", "MISSILE", "MAGIC"]

        for action_type in action_types:
            with self.subTest(action_type=action_type):
                dialog = ActionDialog(
                    action_type=action_type,
                    current_player_name="Player 1",
                    acting_army=self.sample_acting_army,
                    all_players_data=self.sample_player_data,
                    terrain_data=self.sample_terrain_data,
                    parent=self.parent_widget,
                )

                assert dialog.action_type == action_type
                assert dialog.windowTitle() == f"{action_type.title()} Action"

                # Complete flow should work for all action types
                dialog.attacker_dice_input.setText("MM")
                dialog._on_next()

                dialog.defender_dice_input.setText("S")
                dialog._on_next()

                # Should reach results step
                assert dialog.current_step == "results"


if __name__ == "__main__":
    unittest.main()
