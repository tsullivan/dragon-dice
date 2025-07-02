from typing import Optional

from PySide6.QtWidgets import QMessageBox, QWidget


class ErrorDialog:
    """Centralized error handling and user notification system."""

    @staticmethod
    def show_error(
        parent: Optional[QWidget],
        title: str,
        message: str,
        details: Optional[str] = None,
    ):
        """Show an error dialog to the user."""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if details:
            msg_box.setDetailedText(details)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def show_warning(
        parent: Optional[QWidget],
        title: str,
        message: str,
        details: Optional[str] = None,
    ):
        """Show a warning dialog to the user."""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if details:
            msg_box.setDetailedText(details)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def show_info(
        parent: Optional[QWidget],
        title: str,
        message: str,
        details: Optional[str] = None,
    ):
        """Show an info dialog to the user."""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if details:
            msg_box.setDetailedText(details)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def ask_question(
        parent: Optional[QWidget],
        title: str,
        question: str,
        details: Optional[str] = None,
    ) -> bool:
        """Ask a yes/no question and return True for Yes, False for No."""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(question)

        if details:
            msg_box.setDetailedText(details)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = msg_box.exec()
        return result == QMessageBox.StandardButton.Yes


class GameError(Exception):
    """Custom exception for game-specific errors."""

    def __init__(self, message: str, details: Optional[str] = None, user_friendly: bool = True):
        super().__init__(message)
        self.message = message
        self.details = details
        self.user_friendly = user_friendly


class ErrorHandler:
    """Context manager and utility for handling errors gracefully."""

    def __init__(self, parent: Optional[QWidget] = None, show_dialogs: bool = True):
        self.parent = parent
        self.show_dialogs = show_dialogs

    def handle_error(self, error: Exception, context: str = "Operation"):
        """Handle an error with appropriate user feedback."""
        if isinstance(error, GameError):
            if error.user_friendly and self.show_dialogs:
                ErrorDialog.show_error(
                    self.parent,
                    f"Dragon Dice - {context} Error",
                    error.message,
                    error.details,
                )
            else:
                print(f"GameError in {context}: {error.message}")
                if error.details:
                    print(f"Details: {error.details}")
        else:
            error_msg = f"An unexpected error occurred during {context.lower()}"
            details = f"Error type: {type(error).__name__}\nError message: {str(error)}"

            if self.show_dialogs:
                ErrorDialog.show_error(self.parent, f"Dragon Dice - {context} Error", error_msg, details)
            else:
                print(f"Error in {context}: {error}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.handle_error(exc_val, "Operation")
            return True  # Suppress the exception
        return False
