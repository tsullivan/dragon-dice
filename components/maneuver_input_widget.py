from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)
from PySide6.QtCore import Signal
from typing import Optional


class ManeuverInputWidget(QWidget):
    """
    A widget for handling maneuver decisions only.
    Shows Yes/No buttons for deciding whether to maneuver.
    If 'Yes' is clicked, the parent view will show the ManeuverDialog.
    """

    maneuver_decision_made = Signal(bool)  # True if yes, False if no

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._maneuver_yes_button = QPushButton("Choose Army & Maneuver: Yes")
        self._maneuver_yes_button.setMaximumWidth(250)  # Limit button width
        self._maneuver_yes_button.clicked.connect(self._on_maneuver_yes)
        self._main_layout.addWidget(self._maneuver_yes_button)

        self._maneuver_no_button = QPushButton("Choose Army & Maneuver: No")
        self._maneuver_no_button.setMaximumWidth(250)  # Limit button width
        self._maneuver_no_button.clicked.connect(self._on_maneuver_no)
        self._main_layout.addWidget(self._maneuver_no_button)

    def _on_maneuver_yes(self):
        """Emit decision signal - parent view will handle showing ManeuverDialog."""
        self.maneuver_decision_made.emit(True)

    def _on_maneuver_no(self):
        """Emit decision signal - parent view will proceed without maneuvering."""
        self.maneuver_decision_made.emit(False)

    def reset_to_decision(self):
        """Reset widget to initial decision state - both buttons visible."""
        # Nothing needed since we only have decision buttons now
        pass
