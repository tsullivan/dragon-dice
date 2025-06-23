from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget # For type hinting parent

class ActiveEffectsWidget(QGroupBox):
    """
    A widget to display a list of active effects in the game.
    """
    def __init__(self, title: str = "Active Effects", parent: Optional['QWidget'] = None):
        super().__init__(title, parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 15, 5, 5) # Margins inside the group box

        self.effects_list_widget = QListWidget()
        self.effects_list_widget.setWordWrap(True) # Allow text to wrap
        
        layout.addWidget(self.effects_list_widget)
        self.setLayout(layout)

    def update_effects(self, effects_strings: List[str]):
        """
        Updates the displayed list of effects.
        Expects a list of strings, where each string is a formatted effect description.
        """
        self.effects_list_widget.clear()
        for effect_str in effects_strings:
            self.effects_list_widget.addItem(QListWidgetItem(effect_str))
