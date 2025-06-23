from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
from typing import Dict, List, Any, Optional

class PlayerSummaryWidget(QGroupBox): # Inherit from QGroupBox for a titled border
    """
    A widget to display a summary of a single player's army and status.
    """
    def __init__(self, player_name: str, parent: Optional[QWidget] = None):
        super().__init__(f"{player_name}'s Army", parent)
        
        self.summary_layout = QVBoxLayout(self)
        self.summary_layout.setContentsMargins(5, 15, 5, 5) # Margins inside the group box

        self.details_label = QLabel("Loading summary...")
        self.details_label.setWordWrap(True)
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.details_label.setStyleSheet("ul { margin-left:0px; padding-left:5px; list-style-position:inside; } li { margin-bottom: 2px; }")
        
        self.summary_layout.addWidget(self.details_label)
        self.setLayout(self.summary_layout)

    def update_summary(self, player_data: Dict[str, Any]):
        """
        Updates the displayed summary based on the provided player data.
        player_data expected keys: 'name', 'captured_terrains', 'terrains_to_win', 'armies' (list of dicts)
        """
        self.setTitle(f"{player_data.get('name', 'N/A')}'s Army") # Update title in case name changes (though unlikely here)

        summary_html = "<ul>"
        summary_html += f"<li>Captured Terrains: {player_data.get('captured_terrains', 0)}/{player_data.get('terrains_to_win', 2)}</li>"
        
        armies = player_data.get('armies', [])
        for army in armies:
            summary_html += f"<li>{army.get('name', 'N/A')}: {army.get('points', 0)}pts (at {army.get('location', 'N/A')})</li>"
        summary_html += "</ul>"
        
        self.details_label.setText(summary_html)
