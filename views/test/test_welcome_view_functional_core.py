from unittest.mock import Mock

import pytest

import constants
from views.welcome_view import WelcomeView


class TestWelcomeViewCoreFunctionality:
    """Core functionality tests for WelcomeView to validate user input capabilities."""

    def test_welcome_view_has_required_ui_elements(self, qtbot):
        """Test that the welcome view has all required UI elements for user input."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        # Verify player count selection exists
        assert hasattr(welcome_view, "player_count_button_group")
        assert len(welcome_view.player_count_button_group.buttons()) == 3

        # Verify force size selection exists
        assert hasattr(welcome_view, "force_size_button_group")
        assert len(welcome_view.force_size_button_group.buttons()) == len(constants.FORCE_SIZE_OPTIONS)

        # Verify proceed button exists
        assert hasattr(welcome_view, "proceed_button")
        assert welcome_view.proceed_button.text() == "Proceed to Player Setup"

    def test_player_count_options_are_correct(self, qtbot):
        """Test that player count options match expected values."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        button_texts = [btn.text() for btn in welcome_view.player_count_button_group.buttons()]
        expected_texts = ["2", "3", "4"]

        for expected in expected_texts:
            assert expected in button_texts, f"Missing player count option: {expected}"

    def test_force_size_options_are_correct(self, qtbot):
        """Test that force size options match expected values."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        button_texts = [btn.text() for btn in welcome_view.force_size_button_group.buttons()]

        for expected_size in constants.FORCE_SIZE_OPTIONS:
            # Check that the button contains the points value and dragon info
            found_button = False
            for button_text in button_texts:
                if f"{expected_size} pts" in button_text and "dragon" in button_text:
                    found_button = True
                    break
            assert found_button, f"Missing force size option with {expected_size} pts"

    def test_default_selections_are_correct(self, qtbot):
        """Test that default selections are as expected."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        # Check player count default (should be 2)
        player_checked = [btn for btn in welcome_view.player_count_button_group.buttons() if btn.isChecked()]
        assert len(player_checked) == 1
        assert player_checked[0].text() == "2"

        # Check force size default (should be DEFAULT_FORCE_SIZE)
        force_checked = [btn for btn in welcome_view.force_size_button_group.buttons() if btn.isChecked()]
        assert len(force_checked) == 1
        assert f"{constants.DEFAULT_FORCE_SIZE} pts" in force_checked[0].text()

    def test_signals_are_defined(self, qtbot):
        """Test that required signals are defined."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        # Verify signals exist
        assert hasattr(welcome_view, "player_count_selected_signal")
        assert hasattr(welcome_view, "force_size_selected_signal")
        assert hasattr(welcome_view, "proceed_signal")

    def test_emit_current_selections_emits_correct_values(self, qtbot):
        """Test that emit_current_selections emits the expected default values."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        # Connect mocks to capture signal values
        player_count_mock = Mock()
        force_size_mock = Mock()
        welcome_view.player_count_selected_signal.connect(player_count_mock)
        welcome_view.force_size_selected_signal.connect(force_size_mock)

        # Trigger emission
        welcome_view.emit_current_selections()

        # Verify correct values were emitted
        player_count_mock.assert_called_with(2)  # Default player count
        force_size_mock.assert_called_with(constants.DEFAULT_FORCE_SIZE)  # Default force size

    def test_proceed_signal_can_be_triggered(self, qtbot):
        """Test that proceed signal can be triggered."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        proceed_mock = Mock()
        welcome_view.proceed_signal.connect(proceed_mock)

        # Manually trigger the proceed signal (simulates button click)
        welcome_view.proceed_signal.emit()

        proceed_mock.assert_called_once()

    def test_user_can_select_all_player_count_options(self, qtbot):
        """Test that user can select each player count option."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        # Test each player count option by setting it as checked
        for expected_count in [2, 3, 4]:
            # Find the button for this count
            target_button = None
            for button in welcome_view.player_count_button_group.buttons():
                button_id = welcome_view.player_count_button_group.id(button)
                if button_id == expected_count:
                    target_button = button
                    break

            assert target_button is not None, f"Could not find button for {expected_count} players"

            # Set it as checked (simulates user selection)
            target_button.setChecked(True)

            # Verify it's the only checked button
            checked_buttons = [btn for btn in welcome_view.player_count_button_group.buttons() if btn.isChecked()]
            assert len(checked_buttons) == 1
            assert checked_buttons[0] == target_button

    def test_user_can_select_all_force_size_options(self, qtbot):
        """Test that user can select each force size option."""
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        # Test each force size option by setting it as checked
        for expected_size in constants.FORCE_SIZE_OPTIONS:
            # Find the button for this size
            target_button = None
            for button in welcome_view.force_size_button_group.buttons():
                button_id = welcome_view.force_size_button_group.id(button)
                if button_id == expected_size:
                    target_button = button
                    break

            assert target_button is not None, f"Could not find button for {expected_size} pts"

            # Set it as checked (simulates user selection)
            target_button.setChecked(True)

            # Verify it's the only checked button
            checked_buttons = [btn for btn in welcome_view.force_size_button_group.buttons() if btn.isChecked()]
            assert len(checked_buttons) == 1
            assert checked_buttons[0] == target_button

    def test_welcome_view_integration_validation(self, qtbot):
        """
        Integration test to validate that the welcome view provides the expected
        user input capabilities: number of players and total force size selection.
        """
        welcome_view = WelcomeView()
        qtbot.addWidget(welcome_view)

        # Test 1: User can see all player count options
        player_options = [btn.text() for btn in welcome_view.player_count_button_group.buttons()]
        assert "2" in player_options
        assert "3" in player_options
        assert "4" in player_options

        # Test 2: User can see all force size options
        force_options = [btn.text() for btn in welcome_view.force_size_button_group.buttons()]
        for size in constants.FORCE_SIZE_OPTIONS:
            found_option = any(f"{size} pts" in option for option in force_options)
            assert found_option, f"Force size {size} pts not found in options: {force_options}"

        # Test 3: User has sensible defaults
        default_player_count = [btn for btn in welcome_view.player_count_button_group.buttons() if btn.isChecked()][0]
        assert default_player_count.text() == "2"

        default_force_size = [btn for btn in welcome_view.force_size_button_group.buttons() if btn.isChecked()][0]
        assert f"{constants.DEFAULT_FORCE_SIZE} pts" in default_force_size.text()

        # Test 4: User can change selections
        # Change to 4 players
        four_player_button = None
        for button in welcome_view.player_count_button_group.buttons():
            if welcome_view.player_count_button_group.id(button) == 4:
                four_player_button = button
                break
        assert four_player_button is not None
        four_player_button.setChecked(True)
        assert four_player_button.isChecked()

        # Change to 60 pts
        sixty_hp_button = None
        for button in welcome_view.force_size_button_group.buttons():
            if welcome_view.force_size_button_group.id(button) == 60:
                sixty_hp_button = button
                break
        assert sixty_hp_button is not None
        sixty_hp_button.setChecked(True)
        assert sixty_hp_button.isChecked()

        # Test 5: User can proceed to next step
        assert welcome_view.proceed_button.isEnabled()
        # Note: Button visibility requires the widget to be shown, but we can test it exists
        assert welcome_view.proceed_button is not None

        # SUCCESS: The welcome view provides both required input capabilities:
