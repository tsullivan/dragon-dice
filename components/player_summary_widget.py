from typing import Any, Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from utils import strict_get, strict_get_optional
from views.display_utils import format_terrain_summary


class PlayerSummaryWidget(QGroupBox):  # Inherit from QGroupBox for a titled border
    """
    A widget to display a summary of a single player's army and status.
    """

    def __init__(self, player_name: str, parent: Optional[QWidget] = None):
        super().__init__(f"{player_name}'s Army", parent)

        self.summary_layout = QVBoxLayout(self)
        self.summary_layout.setContentsMargins(5, 15, 5, 5)  # Margins inside the group box

        self.details_label = QLabel("Loading summary...")
        self.details_label.setWordWrap(True)
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.details_label.setStyleSheet(
            "ul { margin-left:0px; padding-left:5px; list-style-position:inside; } li { margin-bottom: 2px; }"
        )

        self.summary_layout.addWidget(self.details_label)
        self.setLayout(self.summary_layout)

    def update_summary(self, player_data: Dict[str, Any], terrain_data: Optional[Dict[str, Any]] = None):
        """
        Updates the displayed summary based on the provided player data.
        player_data expected keys: 'name', 'captured_terrains', 'terrains_to_win', 'armies' (list of dicts)
        terrain_data: Optional terrain information to determine home vs frontier terrains
        """
        self.setTitle(
            f"{strict_get(player_data, 'name')}'s Army"
        )  # Update title in case name changes (though unlikely here)

        summary_html = "<ul>"
        summary_html += f"<li>Captured Terrains: {player_data.get('captured_terrains', 0)}/{player_data.get('terrains_to_win', 2)}</li>"

        armies = strict_get(player_data, "armies")
        for army in armies:
            army_type = strict_get(army, "army_type")
            army_points = strict_get(army, "points")
            army_location = strict_get(army, "location")

            # Use the army's display_name if available, otherwise use army_type
            formatted_army_type = army.get("display_name", army_type.title())

            # Format location using utility function for consistency with Available Armies
            if terrain_data and army_location in terrain_data:
                terrain_info = terrain_data[army_location]
                terrain_type = strict_get(terrain_info, "type")
                face_number = strict_get(terrain_info, "face")
                terrain_controller = strict_get_optional(terrain_info, "controller")

                # Use standard formatting for consistency
                formatted_location = format_terrain_summary(
                    army_location, terrain_type, face_number, terrain_controller
                )
            else:
                # Fallback formatting when no terrain data
                formatted_location = f"🗺️ {army_location}"

            summary_html += (
                f"<li><b>{formatted_army_type}</b>: {army_points}pts<br>&nbsp;&nbsp;<b>{formatted_location}</b></li>"
            )
        summary_html += "</ul>"

        self.details_label.setText(summary_html)
