from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
from typing import Dict, List, Any, Optional
import constants


class PlayerSummaryWidget(QGroupBox):  # Inherit from QGroupBox for a titled border
    """
    A widget to display a summary of a single player's army and status.
    """

    def __init__(self, player_name: str, parent: Optional[QWidget] = None):
        super().__init__(f"{player_name}'s Army", parent)

        self.summary_layout = QVBoxLayout(self)
        self.summary_layout.setContentsMargins(
            5, 15, 5, 5
        )  # Margins inside the group box

        self.details_label = QLabel("Loading summary...")
        self.details_label.setWordWrap(True)
        self.details_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.details_label.setStyleSheet(
            "ul { margin-left:0px; padding-left:5px; list-style-position:inside; } li { margin-bottom: 2px; }"
        )

        self.summary_layout.addWidget(self.details_label)
        self.setLayout(self.summary_layout)

    def update_summary(
        self, player_data: Dict[str, Any], terrain_data: Dict[str, Any] = None
    ):
        """
        Updates the displayed summary based on the provided player data.
        player_data expected keys: 'name', 'captured_terrains', 'terrains_to_win', 'armies' (list of dicts)
        terrain_data: Optional terrain information to determine home vs frontier terrains
        """
        self.setTitle(
            f"{player_data.get('name', 'N/A')}'s Army"
        )  # Update title in case name changes (though unlikely here)

        summary_html = "<ul>"
        summary_html += f"<li>Captured Terrains: {player_data.get('captured_terrains', 0)}/{player_data.get('terrains_to_win', 2)}</li>"

        armies = player_data.get("armies", [])
        for army in armies:
            army_name = army.get("name", "N/A")
            army_points = army.get("points", 0)
            army_location = army.get("location", "N/A")

            # Make location very prominent with bold formatting and terrain type description
            location_icon = "🗺️"  # Default terrain icon
            terrain_description = ""

            # Get terrain icon from constants
            for terrain_name, icon in constants.TERRAIN_ICONS.items():
                if terrain_name in army_location:
                    location_icon = icon
                    break

            # Add home terrain designation using terrain data if available
            if terrain_data and army_location in terrain_data:
                terrain_info = terrain_data[army_location]
                terrain_type = terrain_info.get("type", "")
                terrain_controller = terrain_info.get("controller", "")

                if terrain_type == "Frontier":
                    terrain_description = " (Frontier Terrain)"
                elif terrain_type == "Home" and terrain_controller:
                    terrain_description = f" ({terrain_controller}'s Home Terrain)"
                elif terrain_type == "Home":
                    terrain_description = " (Home Terrain)"
            elif terrain_description == "":  # Fallback if no terrain data
                # Try to guess from common terrain names
                if "Flatland" in army_location:
                    terrain_description = " (Frontier Terrain)"
                else:
                    terrain_description = " (Home Terrain)"

            summary_html += f"<li><b>{army_name}</b>: {army_points}pts<br>&nbsp;&nbsp;LOCATION: <b>{location_icon} {army_location}{terrain_description}</b></li>"
        summary_html += "</ul>"

        self.details_label.setText(summary_html)
