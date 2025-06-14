from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                               QLineEdit, QGroupBox)
from PySide6.QtCore import Qt, Signal
from typing import List, Optional, Any

from components.carousel import CarouselInputWidget

class PlayerIdentityWidget(QWidget):
    """
    A widget for setting up a player's name, home terrain, and proposed frontier terrain.
    """
    name_changed = Signal(str)
    home_terrain_changed = Signal(str) # Emits terrain name
    frontier_proposal_changed = Signal(str) # Emits terrain name

    def __init__(self, player_display_number: int, all_terrain_options: List[str], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.all_terrain_options = all_terrain_options

        layout = QFormLayout(self)
        layout.setContentsMargins(0,0,0,0) # No external margins, let parent handle
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # Player Name
        self.player_name_input = QLineEdit()
        self.player_name_input.setPlaceholderText(f"Player {player_display_number} Name")
        self.player_name_input.textChanged.connect(self.name_changed.emit)
        layout.addRow("Player Name:", self.player_name_input)

        # Home Terrain
        self.home_terrain_carousel = CarouselInputWidget(
            allowed_values=self.all_terrain_options,
            initial_value=self.all_terrain_options[0] if self.all_terrain_options else None
        )
        self.home_terrain_carousel.valueChanged.connect(self._emit_home_terrain_changed)
        layout.addRow("Home Terrain:", self.home_terrain_carousel)

        # Proposed Frontier Terrain
        self.proposed_terrain_carousel = CarouselInputWidget(
            allowed_values=self.all_terrain_options,
            initial_value=self.all_terrain_options[0] if self.all_terrain_options else None
        )
        self.proposed_terrain_carousel.valueChanged.connect(self._emit_frontier_proposal_changed)
        layout.addRow("Proposed Frontier Terrain:", self.proposed_terrain_carousel)

    def _emit_home_terrain_changed(self, value: Any):
        if isinstance(value, str): # Assuming terrain names are strings
            self.home_terrain_changed.emit(value)

    def _emit_frontier_proposal_changed(self, value: Any):
        if isinstance(value, str):
            self.frontier_proposal_changed.emit(value)

    def get_name(self) -> str:
        return self.player_name_input.text().strip()

    def set_name(self, name: str):
        self.player_name_input.setText(name)

    def get_home_terrain(self) -> Optional[str]:
        return self.home_terrain_carousel.value()

    def set_home_terrain(self, terrain_name: Optional[str]):
        self.home_terrain_carousel.setValue(terrain_name)

    def get_frontier_proposal(self) -> Optional[str]:
        return self.proposed_terrain_carousel.value()

    def set_frontier_proposal(self, terrain_name: Optional[str]):
        self.proposed_terrain_carousel.setValue(terrain_name)

    def set_player_display_number(self, number: int):
        self.player_name_input.setPlaceholderText(f"Player {number} Name")

    def clear_inputs(self):
        self.player_name_input.clear()
        if self.all_terrain_options:
            self.home_terrain_carousel.setValue(self.all_terrain_options[0])
            self.proposed_terrain_carousel.setValue(self.all_terrain_options[0])
        else:
            self.home_terrain_carousel.setValue(None)
            self.proposed_terrain_carousel.setValue(None)

