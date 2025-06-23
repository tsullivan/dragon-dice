import pytest
from unittest.mock import Mock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QRadioButton

from views.welcome_view import WelcomeView
import constants


class TestWelcomeViewFunctional:
    """Functional tests for WelcomeView user input validation."""

    def test_player_count_default_selection(self, qtbot):
        """Test that player count has a default selection."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        
        # Check that exactly one button is selected and it's the default (2)
        checked_buttons = [btn for btn in welcome_view.player_count_button_group.buttons() if btn.isChecked()]
        assert len(checked_buttons) == 1
        assert checked_buttons[0].text() == "2"

    def test_force_size_default_selection(self, qtbot):
        """Test that force size has a default selection."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        
        # Check that exactly one button is selected and it's the default
        checked_buttons = [btn for btn in welcome_view.force_size_button_group.buttons() if btn.isChecked()]
        assert len(checked_buttons) == 1
        assert f"{constants.DEFAULT_FORCE_SIZE} HP" in checked_buttons[0].text()

    def test_all_force_size_options_available(self, qtbot):
        """Test that all expected force size options are available."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        
        # Get all force size button texts
        button_texts = [button.text() for button in welcome_view.force_size_button_group.buttons()]
        
        # Verify all expected options are present
        expected_options = [f"{size} HP" for size in constants.FORCE_SIZE_OPTIONS]
        for expected_option in expected_options:
            assert expected_option in button_texts

    def test_all_player_count_options_available(self, qtbot):
        """Test that all expected player count options are available."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        
        # Get all player count button texts
        button_texts = [button.text() for button in welcome_view.player_count_button_group.buttons()]
        
        # Verify expected player counts are present (2, 3, 4)
        expected_counts = ["2", "3", "4"]
        for expected_count in expected_counts:
            assert expected_count in button_texts

    def test_player_count_selection_state_change(self, qtbot):
        """Test that player count selection changes UI state correctly."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        welcome_view.show()
        qtbot.waitExposed(welcome_view)
        
        # Find the 3 players button and click it
        target_button = None
        for button in welcome_view.player_count_button_group.buttons():
            if button.text() == "3":
                target_button = button
                break
        
        assert target_button is not None, "Could not find 3 players button"
        
        # Use setChecked instead of mouseClick for more reliable testing
        target_button.setChecked(True)
        
        # Verify the button is now checked
        assert target_button.isChecked()
        
        # Verify only one button is checked
        checked_buttons = [btn for btn in welcome_view.player_count_button_group.buttons() if btn.isChecked()]
        assert len(checked_buttons) == 1
        assert checked_buttons[0] == target_button

    def test_force_size_selection_state_change(self, qtbot):
        """Test that force size selection changes UI state correctly."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        welcome_view.show()
        qtbot.waitExposed(welcome_view)
        
        # Find the 36 HP button and click it
        target_button = None
        for button in welcome_view.force_size_button_group.buttons():
            if "36 HP" in button.text():
                target_button = button
                break
        
        assert target_button is not None, "Could not find 36 HP button"
        
        # Simulate user click
        qtbot.mouseClick(target_button, Qt.LeftButton)
        
        # Verify the button is now checked
        assert target_button.isChecked()
        
        # Verify only one button is checked
        checked_buttons = [btn for btn in welcome_view.force_size_button_group.buttons() if btn.isChecked()]
        assert len(checked_buttons) == 1
        assert checked_buttons[0] == target_button

    def test_proceed_button_exists_and_clickable(self, qtbot):
        """Test that proceed button exists and can be clicked."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        welcome_view.show()
        qtbot.waitExposed(welcome_view)
        
        # Verify proceed button exists
        assert hasattr(welcome_view, 'proceed_button')
        assert welcome_view.proceed_button.text() == "Proceed to Player Setup"
        
        # Verify button is enabled and clickable
        assert welcome_view.proceed_button.isEnabled()
        
        # Connect a mock to test signal emission
        proceed_mock = Mock()
        welcome_view.proceed_signal.connect(proceed_mock)
        
        # Click the proceed button
        qtbot.mouseClick(welcome_view.proceed_button, Qt.LeftButton)
        
        # Verify proceed signal was emitted
        proceed_mock.assert_called_once()

    def test_emit_current_selections_works(self, qtbot):
        """Test that emit_current_selections method works correctly."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        
        # Connect mocks to capture signals
        player_count_mock = Mock()
        force_size_mock = Mock()
        welcome_view.player_count_selected_signal.connect(player_count_mock)
        welcome_view.force_size_selected_signal.connect(force_size_mock)
        
        # Call emit_current_selections
        welcome_view.emit_current_selections()
        
        # Verify both signals were emitted with default values
        player_count_mock.assert_called_with(2)  # Default player count
        force_size_mock.assert_called_with(constants.DEFAULT_FORCE_SIZE)  # Default force size

    def test_ui_has_both_selection_groups(self, qtbot):
        """Test that UI contains both player count and force size selection groups."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        
        # Verify both button groups exist
        assert hasattr(welcome_view, 'player_count_button_group')
        assert hasattr(welcome_view, 'force_size_button_group')
        
        # Verify button groups have buttons
        assert len(welcome_view.player_count_button_group.buttons()) > 0
        assert len(welcome_view.force_size_button_group.buttons()) > 0
        
        # Verify button groups have the expected number of buttons
        assert len(welcome_view.player_count_button_group.buttons()) == 3  # 2, 3, 4 players
        assert len(welcome_view.force_size_button_group.buttons()) == len(constants.FORCE_SIZE_OPTIONS)

    def test_selections_work_independently(self, qtbot):
        """Test that player count and force size selections work independently."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)
        welcome_view.show()
        qtbot.waitExposed(welcome_view)
        
        # Change player count to 4
        player_button = None
        for button in welcome_view.player_count_button_group.buttons():
            if button.text() == "4":
                player_button = button
                break
        assert player_button is not None
        player_button.setChecked(True)
        
        # Change force size to 60
        force_button = None
        for button in welcome_view.force_size_button_group.buttons():
            if "60 HP" in button.text():
                force_button = button
                break
        assert force_button is not None
        force_button.setChecked(True)
        
        # Verify both selections are correct
        assert player_button.isChecked()
        assert force_button.isChecked()
        
        # Verify other buttons are not checked
        for button in welcome_view.player_count_button_group.buttons():
            if button != player_button:
                assert not button.isChecked()
        
        for button in welcome_view.force_size_button_group.buttons():
            if button != force_button:
                assert not button.isChecked()