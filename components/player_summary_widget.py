from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
from typing import Dict, List, Any, Optional
import utils.constants as constants
from utils.display_utils import format_army_type, format_terrain_summary


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
            army_type = army.get("army_type", "home")  # Default to home army
            army_points = army.get("points", 0)
            army_location = army.get("location", "N/A")

            # Format army with type emoji and proper capitalization
            formatted_army_type = format_army_type(army_type.title())

            # Format location using enhanced utility function
            if terrain_data and army_location in terrain_data:
                terrain_info = terrain_data[army_location]
                terrain_type = terrain_info.get("type", "")
                face_number = terrain_info.get("face", 1)
                terrain_controller = terrain_info.get("controller", "")
                
                # Use custom formatting based on user requirements
                formatted_location = self._format_enhanced_terrain_summary(
                    army_location, terrain_type, face_number, terrain_controller
                )
            else:
                # Fallback formatting when no terrain data
                formatted_location = f"🗺️ {army_location}"

            summary_html += f"<li><b>{formatted_army_type}</b>: {army_points}pts<br>&nbsp;&nbsp;<b>{formatted_location}</b></li>"
        summary_html += "</ul>"

        self.details_label.setText(summary_html)

    def _format_enhanced_terrain_summary(
        self, terrain_name: str, terrain_type: str, face_number: int, controller: str = None
    ) -> str:
        """
        Format terrain summary according to user requirements with proper icons and structure.
        
        Examples:
        - "[frontier_icon] Frontier Terrain: [color_icon1][color_icon2] Coastland (Face 1)"
        - "[home_icon] Player 1's Home: [color_icon1][color_icon2] Coastland (Face 1)" 
        """
        import utils.constants as constants
        
        # Extract the base terrain name (e.g., "Coastland" from "Player 1 Coastland")
        clean_name = terrain_name
        if " " in terrain_name:
            parts = terrain_name.split()
            if len(parts) >= 3 and parts[0] == "Player":
                # Extract terrain type from "Player X Coastland" -> "Coastland"
                base_terrain = " ".join(parts[2:])
                
                # Use DISPLAY_NAME from TERRAIN_DATA if available
                terrain_key = base_terrain.upper()
                if terrain_key in constants.TERRAIN_DATA:
                    clean_name = constants.TERRAIN_DATA[terrain_key]["DISPLAY_NAME"]
                else:
                    clean_name = base_terrain
            else:
                # Check if it's a known terrain type
                terrain_key = terrain_name.upper()
                if terrain_key in constants.TERRAIN_DATA:
                    clean_name = constants.TERRAIN_DATA[terrain_key]["DISPLAY_NAME"]
        else:
            # Single word terrain name - check TERRAIN_DATA
            terrain_key = terrain_name.upper()
            if terrain_key in constants.TERRAIN_DATA:
                clean_name = constants.TERRAIN_DATA[terrain_key]["DISPLAY_NAME"]
        
        # Get terrain-specific icon
        terrain_icon = constants.get_terrain_or_location_icon(terrain_type)
        
        # Get color icons for the terrain (placeholder for now)
        # In a full implementation, this would come from terrain color data
        color_icons = "🔵🟢"  # Placeholder - should be actual terrain colors
        
        if terrain_type.upper() == "FRONTIER":
            return f"{terrain_icon} Frontier Terrain: {color_icons} {clean_name} (Face {face_number})"
        elif controller and terrain_type.upper() == "HOME":
            home_icon = constants.get_terrain_or_location_icon("Home") 
            return f"{home_icon} {controller}'s Home: {color_icons} {clean_name} (Face {face_number})"
        else:
            return f"{terrain_icon} {clean_name}: {color_icons} (Face {face_number})"
