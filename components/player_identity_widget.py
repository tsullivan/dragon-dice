# components/player_identity_widget.py
from PySide6.QtWidgets import QWidget, QLineEdit
from PySide6.QtCore import Signal, Slot
from typing import Optional


class PlayerIdentityWidget(QWidget):
    """
    A widget for setting up player name.
    """

    name_changed = Signal(str)

    def __init__(self, player_display_number_for_placeholder: int, parent=None):
        super().__init__(parent)

        # Player Name
        self.player_name_input = QLineEdit()
        self.player_name_input.setMaximumWidth(250)  # Prevent excessive stretching
        self.player_name_input.setPlaceholderText(
            f"Enter Player {player_display_number_for_placeholder}'s Name"
        )
        self.player_name_input.textChanged.connect(self.name_changed.emit)

        # The layout will now be managed by PlayerSetupView's QGridLayout
        # This widget primarily provides the input fields and their signals.

    def get_name(self) -> str:
        return self.player_name_input.text()

    def set_name(self, name: str):
        self.player_name_input.setText(name)

    def clear_inputs(self):
        """Clears the name input and resets carousels to their default (first item)."""
        self.player_name_input.clear()

    def set_default_name(self, player_num: int):
        """Sets the default player name based on the player number."""
        default_name = f"Player {player_num}"
        self.player_name_input.setText(default_name)

    def set_player_display_number(self, player_num: int):
        """Updates the placeholder text for the player name input."""
        self.player_name_input.setPlaceholderText(f"Enter Player {player_num}'s Name")
