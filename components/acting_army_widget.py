from typing import Any, Dict, List, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from utils.display_utils import format_army_type, format_terrain_summary


class ActingArmyWidget(QWidget):
    """
    A widget for choosing which army will be the acting army for the March phase.
    This choice persists through both Maneuver and Action steps.
    """

    acting_army_chosen = Signal(dict)  # Emits the chosen army data

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        self.title_label = QLabel("Choose Acting Army for March Phase")
        title_font = self.title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self._main_layout.addWidget(self.title_label)

        # Instructions
        self.instruction_label = QLabel("Select which army will be active for both Maneuver and Action steps:")
        self.instruction_label.setWordWrap(True)
        self._main_layout.addWidget(self.instruction_label)

        # Army selection group
        self.army_group = QGroupBox("Available Armies")
        self.army_layout = QVBoxLayout(self.army_group)
        self._main_layout.addWidget(self.army_group)

        # Button group for radio buttons
        self.army_button_group = QButtonGroup(self)

        # Will be populated when armies are set
        self.available_armies: List[Dict[str, Any]] = []
        self.selected_army = None

    def set_available_armies(self, armies: List[Dict[str, Any]], terrain_data: Optional[Dict[str, Any]] = None):
        """Set the available armies for selection."""
        self.available_armies = armies

        # Clear existing radio buttons
        for button in self.army_button_group.buttons():
            self.army_button_group.removeButton(button)
            button.deleteLater()

        # Clear layout
        for i in reversed(range(self.army_layout.count())):
            child = self.army_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add radio buttons for each army
        for i, army_info in enumerate(armies):
            army_name = army_info.get("name", "Unknown Army")
            army_type = army_info.get("army_type", "Home")  # Default to Home
            location = army_info.get("location", "Unknown")
            unit_count = len(army_info.get("units", []))

            # Format army using utility function
            formatted_army = format_army_type(army_type)

            # Format location using utility function
            if terrain_data and location in terrain_data:
                terrain_info = terrain_data[location]
                terrain_type = terrain_info.get("type", "")
                terrain_face = terrain_info.get("face", 1)
                terrain_controller = terrain_info.get("controller", "")

                formatted_location = format_terrain_summary(location, terrain_type, terrain_face, terrain_controller)
            else:
                # Fallback formatting when no terrain data
                formatted_location = f"🗺️ {location}"

            button_text = (
                f"{formatted_army} {army_name}\nLOCATION: {formatted_location}\nUNITS: {unit_count} units available"
            )

            radio_button = QRadioButton(button_text)
            self.army_button_group.addButton(radio_button, i)
            self.army_layout.addWidget(radio_button)

        # Connect signal for selection changes
        self.army_button_group.idClicked.connect(self._on_army_selected)

        # Confirm button
        self.confirm_button = QPushButton("Confirm Acting Army Selection")
        self.confirm_button.setMaximumWidth(300)
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.army_layout.addWidget(self.confirm_button)

        # Auto-select first army if available
        if armies and self.army_button_group.buttons():
            self.army_button_group.buttons()[0].setChecked(True)
            self.selected_army = armies[0]

    def _on_army_selected(self, army_index: int):
        """Handle army selection."""
        if 0 <= army_index < len(self.available_armies):
            self.selected_army = self.available_armies[army_index]
            if self.selected_army:
                print(f"Acting army selected: {self.selected_army.get('name')} at {self.selected_army.get('location')}")

    def get_selected_army(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected army."""
        return self.selected_army

    def confirm_selection(self):
        """Emit the selected army choice."""
        if self.selected_army:
            self.acting_army_chosen.emit(self.selected_army)
        else:
            print("No army selected!")
