from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Signal
from typing import Optional, Dict, Any
import utils.constants as constants


class ActionDecisionWidget(QWidget):
    """
    A widget for deciding whether to take an action with the acting army.
    Shows available actions based on the terrain die face where the army is located.
    """

    action_decision_made = Signal(bool)  # True if yes, False if no

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        self.title_label = QLabel("Take Action with Acting Army?")
        title_font = self.title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self._main_layout.addWidget(self.title_label)

        # Army info display
        self.army_info_label = QLabel("Acting Army: (Not set)")
        self.army_info_label.setWordWrap(True)
        self._main_layout.addWidget(self.army_info_label)

        # Available actions info
        self.actions_info_label = QLabel("Available actions will be shown here...")
        self.actions_info_label.setWordWrap(True)
        self.actions_info_label.setStyleSheet(
            "background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc; border-radius: 4px;"
        )
        self._main_layout.addWidget(self.actions_info_label)

        # Decision buttons
        button_layout = QHBoxLayout()

        self.action_yes_button = QPushButton("Take Action: Yes")
        self.action_yes_button.setMaximumWidth(200)
        self.action_yes_button.clicked.connect(self._on_action_yes)
        button_layout.addWidget(self.action_yes_button)

        self.action_no_button = QPushButton("Take Action: No")
        self.action_no_button.setMaximumWidth(200)
        self.action_no_button.clicked.connect(self._on_action_no)
        button_layout.addWidget(self.action_no_button)

        self._main_layout.addLayout(button_layout)

    def set_acting_army(
        self, army_data: Dict[str, Any], terrain_data: Dict[str, Any] = None
    ):
        """Set the acting army and show available actions based on terrain die face."""
        try:
            army_name = army_data.get("name", "Unknown Army")
            army_type = army_data.get("army_type", "unknown")
            location = army_data.get("location", "Unknown")
            unit_count = len(army_data.get("units", []))

            # Add terrain icon
            location_icon = ""
            for terrain_name, terrain_info in constants.TERRAIN_DATA.items():
                if terrain_name in location:
                    location_icon = terrain_info.get_color_string()
                    break
            if not location_icon:
                location_icon = "🗺️"  # Default terrain icon

            # Add army type indicator
            try:
                army_type_indicator = constants.get_army_type_icon(army_type)
            except KeyError:
                army_type_indicator = "⚔️"

            # Update army info display
            self.army_info_label.setText(
                f"Acting Army: {army_type_indicator} {army_name}\n"
                f"Location: {location_icon} {location} ({unit_count} units)"
            )

            # Get terrain die face and determine available actions
            terrain_die_face = 1  # Default
            terrain_description = ""

            if terrain_data and location in terrain_data:
                terrain_info = terrain_data[location]
                terrain_die_face = terrain_info.get("face", 1)
                terrain_type = terrain_info.get("type", "")
                terrain_controller = terrain_info.get("controller", "")

                if terrain_type == "Frontier":
                    terrain_description = f" (Frontier Terrain)"
                elif terrain_type == "Home" and terrain_controller:
                    terrain_description = f" ({terrain_controller}'s Home Terrain)"
                else:
                    terrain_description = f" (Home Terrain)"

            # Determine available actions based on terrain die face
            available_actions = self._get_available_actions(terrain_die_face)

            actions_text = (
                f"TERRAIN DIE FACE: {terrain_die_face}{terrain_description}\n\n"
                f"AVAILABLE ACTIONS (based on terrain die face {terrain_die_face}):\n"
            )

            if available_actions:
                for action in available_actions:
                    actions_text += f"• {action}\n"
            else:
                actions_text += "• No actions available at this terrain die face"

            self.actions_info_label.setText(actions_text)
            
        except Exception as e:
            print(f"Error in ActionDecisionWidget.set_acting_army: {e}")
            # Set fallback values to prevent crashes
            self.army_info_label.setText("Acting Army: Error loading army data")
            self.actions_info_label.setText("Error: Could not load terrain action data")

    def _get_available_actions(self, terrain_die_face: int) -> list:
        """
        Determine available actions based on terrain die face.
        This is a simplified version - in the full game this would be more complex.
        """
        actions = []

        # Basic actions available based on die face
        if terrain_die_face >= 1:
            actions.append("⚔️ MELEE (Close combat attack)")

        if terrain_die_face >= 2:
            actions.append("🏹 MISSILE (Ranged attack)")

        if terrain_die_face >= 3:
            actions.append("✨ MAGIC (Spell casting)")

        # Higher faces might unlock special actions in the full game
        if terrain_die_face >= 5:
            actions.append("💎 SPECIAL (Advanced tactical actions)")

        return actions

    def _on_action_yes(self):
        """Handle Yes button click."""
        print("Player chose to take an action")
        self.action_decision_made.emit(True)

    def _on_action_no(self):
        """Handle No button click."""
        print("Player chose not to take an action")
        self.action_decision_made.emit(False)
