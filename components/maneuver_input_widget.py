from typing import Any, Dict, Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ManeuverInputWidget(QWidget):
    """
    A widget for handling maneuver decisions with acting army display.
    Shows the selected acting army and Yes/No buttons for deciding whether to maneuver.
    If 'Yes' is clicked, the parent view will show the ManeuverDialog.
    """

    maneuver_decision_made = Signal(bool)  # True if yes, False if no

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Main vertical layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(5, 5, 5, 5)

        # Acting army display group
        self._army_group = QGroupBox("Acting Army for Maneuver")
        army_layout = QVBoxLayout(self._army_group)

        self._army_info_label = QLabel("No acting army selected")
        self._army_info_label.setWordWrap(True)
        army_font = QFont()
        army_font.setPointSize(10)
        self._army_info_label.setFont(army_font)
        army_layout.addWidget(self._army_info_label)

        self._main_layout.addWidget(self._army_group)

        # Decision buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 5, 0, 0)

        self._maneuver_yes_button = QPushButton("Maneuver: Yes")
        self._maneuver_yes_button.setMaximumWidth(200)
        self._maneuver_yes_button.setStyleSheet(
            "QPushButton { background-color: #51cf66; color: white; font-weight: bold; }"
        )
        self._maneuver_yes_button.clicked.connect(self._on_maneuver_yes)
        button_layout.addWidget(self._maneuver_yes_button)

        self._maneuver_no_button = QPushButton("Maneuver: No")
        self._maneuver_no_button.setMaximumWidth(200)
        self._maneuver_no_button.setStyleSheet(
            "QPushButton { background-color: #868e96; color: white; font-weight: bold; }"
        )
        self._maneuver_no_button.clicked.connect(self._on_maneuver_no)
        button_layout.addWidget(self._maneuver_no_button)

        self._main_layout.addLayout(button_layout)

    def set_acting_army(self, acting_army: Dict[str, Any], terrain_data: Optional[Dict[str, Any]] = None):
        """Set the acting army information to display."""
        if not acting_army:
            self._army_info_label.setText("No acting army selected")
            return

        army_name = acting_army.get("name", "Unknown Army")
        location = acting_army.get("location", "Unknown Location")
        units = acting_army.get("units", [])
        unit_count = len(units)

        # Get terrain information
        terrain_info = ""
        if terrain_data and location in terrain_data:
            terrain = terrain_data[location]
            face = terrain.get("face", 1)
            terrain_type = terrain.get("type", "Unknown")
            terrain_info = f"\nTerrain: {terrain_type}, Face {face}"

        army_text = f"Army: {army_name}\nLocation: {location}\nUnits: {unit_count}{terrain_info}"

        self._army_info_label.setText(army_text)

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
