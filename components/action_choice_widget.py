from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Signal
from typing import Optional, Dict, Any
import constants


class ActionChoiceWidget(QWidget):
    """
    A widget for selecting an action type (Melee, Missile, Magic).
    Only shows actions available based on terrain die face.
    """

    action_selected = Signal(str)  # Emits "MELEE", "MISSILE", or "MAGIC"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        self.title_label = QLabel("Select Action")
        title_font = self.title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        main_layout.addWidget(self.title_label)

        # Info about terrain limitations
        self.terrain_info_label = QLabel("Available actions based on terrain die face:")
        self.terrain_info_label.setWordWrap(True)
        main_layout.addWidget(self.terrain_info_label)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.melee_button = QPushButton(constants.format_action_display("Melee Action"))
        self.melee_button.setMaximumWidth(150)
        self.melee_button.clicked.connect(lambda: self._emit_action_signal("MELEE"))
        button_layout.addWidget(self.melee_button)

        self.missile_button = QPushButton(
            constants.format_action_display("Missile Action")
        )
        self.missile_button.setMaximumWidth(150)
        self.missile_button.clicked.connect(
            lambda: self._emit_action_signal("MISSILE")
        )
        button_layout.addWidget(self.missile_button)

        self.magic_button = QPushButton(constants.format_action_display("Magic Action"))
        self.magic_button.setMaximumWidth(150)
        self.magic_button.clicked.connect(lambda: self._emit_action_signal("MAGIC"))
        button_layout.addWidget(self.magic_button)

        # Add Skip Action button
        self.skip_button = QPushButton("Skip Action")
        self.skip_button.setMaximumWidth(150)
        self.skip_button.setStyleSheet(
            "QPushButton { background-color: #868e96; color: white; font-weight: bold; }"
        )
        self.skip_button.clicked.connect(lambda: self._emit_action_signal("SKIP"))
        button_layout.addWidget(self.skip_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def set_available_actions(
        self, acting_army: Dict[str, Any], terrain_data: Dict[str, Any] = None
    ):
        """Set which actions are available based on the acting army's terrain die face."""
        location = acting_army.get("location", "Unknown")
        terrain_die_face = 1  # Default

        # Get terrain die face
        if terrain_data and location in terrain_data:
            terrain_info = terrain_data[location]
            terrain_die_face = terrain_info.get("face", 1)
            terrain_type = terrain_info.get("type", "")
            terrain_controller = terrain_info.get("controller", "")

            # Update terrain info display
            if terrain_type == "Frontier":
                terrain_description = f" (Frontier Terrain)"
            elif terrain_type == "Home" and terrain_controller:
                terrain_description = f" ({terrain_controller}'s Home Terrain)"
            else:
                terrain_description = f" (Home Terrain)"

            self.terrain_info_label.setText(
                f"Terrain Die Face: {terrain_die_face}{terrain_description}\n"
                f"Available actions based on face {terrain_die_face}:"
            )
        else:
            self.terrain_info_label.setText(
                f"Terrain Die Face: {terrain_die_face} (Unknown terrain)"
            )

        # Show/hide buttons based on terrain die face
        # Face 1+: Melee available
        self.melee_button.setVisible(terrain_die_face >= 1)

        # Face 2+: Missile available
        self.missile_button.setVisible(terrain_die_face >= 2)

        # Face 3+: Magic available
        self.magic_button.setVisible(terrain_die_face >= 3)

        # Skip button is always visible
        self.skip_button.setVisible(True)

        print(f"[ActionChoiceWidget] Set available actions - Terrain face: {terrain_die_face}")
        print(f"[ActionChoiceWidget] Button visibility - Melee: {self.melee_button.isVisible()}, Missile: {self.missile_button.isVisible()}, Magic: {self.magic_button.isVisible()}, Skip: {self.skip_button.isVisible()}")

    def _emit_action_signal(self, action_type: str):
        """Debug wrapper for action signal emission."""
        print(f"[ActionChoiceWidget] Button clicked: {action_type}")
        self.action_selected.emit(action_type)
        print(f"[ActionChoiceWidget] Signal emitted: {action_type}")
