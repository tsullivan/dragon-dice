import unittest
from unittest.mock import Mock, patch
from components.error_dialog import ErrorDialog, GameError, ErrorHandler


class TestErrorDialog(unittest.TestCase):
    """Test error dialog functionality."""

    def test_game_error_creation(self):
        """Test GameError exception creation."""
        error = GameError("Test error", "Test details", user_friendly=True)

        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.details, "Test details")
        self.assertTrue(error.user_friendly)
        self.assertEqual(str(error), "Test error")

    def test_game_error_defaults(self):
        """Test GameError default values."""
        error = GameError("Test error")

        self.assertEqual(error.message, "Test error")
        self.assertIsNone(error.details)
        self.assertTrue(error.user_friendly)

    @patch("components.error_dialog.QMessageBox")
    def test_show_error_dialog(self, mock_msgbox):
        """Test showing error dialog."""
        mock_box = Mock()
        mock_msgbox.return_value = mock_box

        ErrorDialog.show_error(None, "Test Title", "Test Message", "Test Details")

        mock_msgbox.assert_called_once_with(None)
        mock_box.setIcon.assert_called_once()
        mock_box.setWindowTitle.assert_called_once_with("Test Title")
        mock_box.setText.assert_called_once_with("Test Message")
        mock_box.setDetailedText.assert_called_once_with("Test Details")
        mock_box.exec.assert_called_once()

    @patch("components.error_dialog.QMessageBox")
    def test_show_warning_dialog(self, mock_msgbox):
        """Test showing warning dialog."""
        mock_box = Mock()
        mock_msgbox.return_value = mock_box

        ErrorDialog.show_warning(None, "Warning Title", "Warning Message")

        mock_msgbox.assert_called_once_with(None)
        mock_box.setIcon.assert_called_once()
        mock_box.setWindowTitle.assert_called_once_with("Warning Title")
        mock_box.setText.assert_called_once_with("Warning Message")
        mock_box.exec.assert_called_once()

    def test_error_handler_context_manager(self):
        """Test ErrorHandler as context manager."""
        handler = ErrorHandler(show_dialogs=False)

        with patch("builtins.print") as mock_print:
            with handler:
                raise GameError("Test error", "Test details")

            mock_print.assert_called()

    def test_error_handler_with_regular_exception(self):
        """Test ErrorHandler with regular Python exceptions."""
        handler = ErrorHandler(show_dialogs=False)

        with patch("builtins.print") as mock_print:
            with handler:
                raise ValueError("Test value error")

            mock_print.assert_called()


if __name__ == "__main__":
    unittest.main()
