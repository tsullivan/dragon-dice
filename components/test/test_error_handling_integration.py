import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

from PySide6.QtWidgets import QApplication, QWidget

from components.error_dialog import ErrorDialog, ErrorHandler, GameError


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling integration across the application."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for widget tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        self.parent_widget = QWidget()

    def tearDown(self):
        """Clean up after tests."""
        self.parent_widget.close()

    def test_game_error_with_details(self):
        """Test GameError creation with detailed information."""
        error = GameError(
            "Test game error occurred",
            "Detailed error information for debugging",
            user_friendly=True,
        )

        assert error.message == "Test game error occurred"
        assert error.details == "Detailed error information for debugging"
        assert error.user_friendly
        assert str(error) == "Test game error occurred"

    def test_game_error_minimal(self):
        """Test GameError creation with minimal information."""
        error = GameError("Simple error")

        assert error.message == "Simple error"
        assert error.details is None
        assert error.user_friendly  # Default value

    def test_error_handler_game_error_with_dialogs(self):
        """Test ErrorHandler handling GameError with dialog display."""
        handler = ErrorHandler(self.parent_widget, show_dialogs=True)

        with patch.object(ErrorDialog, "show_error") as mock_show_error:
            handler.handle_error(GameError("Test error", "Test details"), "Test Context")

            mock_show_error.assert_called_once_with(
                self.parent_widget,
                "Dragon Dice - Test Context Error",
                "Test error",
                "Test details",
            )

    def test_error_handler_game_error_no_dialogs(self):
        """Test ErrorHandler handling GameError without dialog display."""
        handler = ErrorHandler(self.parent_widget, show_dialogs=False)

        with patch("builtins.print") as mock_print:
            handler.handle_error(GameError("Test error", "Test details"), "Test Context")

            mock_print.assert_called()

    def test_error_handler_regular_exception_with_dialogs(self):
        """Test ErrorHandler handling regular exceptions with dialog display."""
        handler = ErrorHandler(self.parent_widget, show_dialogs=True)

        with patch.object(ErrorDialog, "show_error") as mock_show_error:
            handler.handle_error(ValueError("Test value error"), "Test Context")

            mock_show_error.assert_called_once()
            call_args = mock_show_error.call_args[0]

            assert call_args[0] == self.parent_widget
            assert call_args[1] == "Dragon Dice - Test Context Error"
            assert "unexpected error" in call_args[2]
            assert "ValueError" in call_args[3]

    def test_error_handler_context_manager_success(self):
        """Test ErrorHandler as context manager with successful operation."""
        handler = ErrorHandler(self.parent_widget, show_dialogs=False)

        with patch("builtins.print") as mock_print:
            with handler:
                # No exception should occur
                result = 2 + 2

            assert result == 4
            mock_print.assert_not_called()

    def test_error_handler_context_manager_exception(self):
        """Test ErrorHandler as context manager with exception handling."""
        handler = ErrorHandler(self.parent_widget, show_dialogs=False)

        with patch("builtins.print") as mock_print:
            with handler:
                raise GameError("Context manager test error")

            mock_print.assert_called()

    def test_error_handler_context_manager_suppresses_exception(self):
        """Test that ErrorHandler context manager suppresses exceptions."""
        handler = ErrorHandler(self.parent_widget, show_dialogs=False)

        exception_raised = False
        try:
            with handler:
                raise ValueError("This should be suppressed")
        except ValueError:
            exception_raised = True

        assert not exception_raised

    @patch("components.error_dialog.QMessageBox")
    def test_error_dialog_show_error_with_details(self, mock_msgbox):
        """Test ErrorDialog.show_error with detailed information."""
        mock_box = Mock()
        mock_msgbox.return_value = mock_box

        ErrorDialog.show_error(
            self.parent_widget,
            "Test Error Title",
            "Test error message",
            "Detailed error information",
        )

        mock_msgbox.assert_called_once_with(self.parent_widget)
        mock_box.setIcon.assert_called_once()
        mock_box.setWindowTitle.assert_called_once_with("Test Error Title")
        mock_box.setText.assert_called_once_with("Test error message")
        mock_box.setDetailedText.assert_called_once_with("Detailed error information")
        mock_box.setStandardButtons.assert_called_once()
        mock_box.exec.assert_called_once()

    @patch("components.error_dialog.QMessageBox")
    def test_error_dialog_show_warning_no_details(self, mock_msgbox):
        """Test ErrorDialog.show_warning without detailed information."""
        mock_box = Mock()
        mock_msgbox.return_value = mock_box

        ErrorDialog.show_warning(self.parent_widget, "Test Warning Title", "Test warning message")

        mock_msgbox.assert_called_once_with(self.parent_widget)
        mock_box.setIcon.assert_called_once()
        mock_box.setWindowTitle.assert_called_once_with("Test Warning Title")
        mock_box.setText.assert_called_once_with("Test warning message")
        mock_box.setDetailedText.assert_not_called()
        mock_box.exec.assert_called_once()

    @patch("components.error_dialog.QMessageBox")
    def test_error_dialog_ask_question_yes(self, mock_msgbox):
        """Test ErrorDialog.ask_question returning True for Yes."""
        mock_box = Mock()
        mock_msgbox.return_value = mock_box
        mock_box.exec.return_value = mock_msgbox.StandardButton.Yes

        result = ErrorDialog.ask_question(
            self.parent_widget,
            "Confirm Action",
            "Are you sure you want to proceed?",
            "This action cannot be undone.",
        )

        assert result
        mock_box.setDetailedText.assert_called_once_with("This action cannot be undone.")

    @patch("components.error_dialog.QMessageBox")
    def test_error_dialog_ask_question_no(self, mock_msgbox):
        """Test ErrorDialog.ask_question returning False for No."""
        mock_box = Mock()
        mock_msgbox.return_value = mock_box
        mock_box.exec.return_value = mock_msgbox.StandardButton.No

        result = ErrorDialog.ask_question(self.parent_widget, "Confirm Action", "Are you sure you want to proceed?")

        assert not result

    def test_error_handler_non_user_friendly_game_error(self):
        """Test ErrorHandler with non-user-friendly GameError."""
        handler = ErrorHandler(self.parent_widget, show_dialogs=True)

        with patch("builtins.print") as mock_print, patch.object(ErrorDialog, "show_error") as mock_show_error:
            handler.handle_error(
                GameError("Internal error", "Debug info", user_friendly=False),
                "Internal",
            )

            # Should print instead of showing dialog
            mock_print.assert_called()
            mock_show_error.assert_not_called()

    def test_error_context_cascading(self):
        """Test error handling with cascading context information."""
        handler = ErrorHandler(show_dialogs=False)

        # Test multiple error handling scenarios
        test_scenarios = [
            (ValueError("Invalid value"), "Input Validation"),
            (KeyError("missing_key"), "Data Access"),
            (FileNotFoundError("file.txt"), "File Operation"),
            (GameError("Game state corrupted"), "Game Logic"),
        ]

        with patch("builtins.print") as mock_print:
            for error, context in test_scenarios:
                handler.handle_error(error, context)

        # Should have handled all errors
        assert mock_print.call_count == len(test_scenarios)


if __name__ == "__main__":
    unittest.main()
