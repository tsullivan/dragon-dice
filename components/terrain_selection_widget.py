# components/terrain_selection_widget.py
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout
from PySide6.QtCore import Signal, Slot
from typing import List, Optional

from .carousel import CarouselInputWidget


class TerrainSelectionWidget(QWidget):
    """
    A widget for selecting Home Terrain and Proposed Frontier Terrain.
    """

    home_terrain_changed = Signal(str)
    frontier_proposal_changed = Signal(str)

    def __init__(self, all_terrain_options: List[str], parent=None):
        super().__init__(parent)
        self.all_terrain_options = all_terrain_options

        layout = QGridLayout(self)

        # Home Terrain Selection
        self.home_terrain_label = QLabel("🏠 Home Terrain:")
        self.home_terrain_carousel = CarouselInputWidget(self.all_terrain_options)
        self.home_terrain_carousel.valueChanged.connect(self.home_terrain_changed.emit)
        self.home_terrain_carousel.valueChanged.connect(self._update_home_terrain_label)
        layout.addWidget(self.home_terrain_label, 0, 0)
        layout.addWidget(self.home_terrain_carousel, 0, 1)

        # Proposed Frontier Terrain Selection
        self.frontier_proposal_label = QLabel("🗺️ Proposed Frontier Terrain:")
        self.frontier_proposal_carousel = CarouselInputWidget(self.all_terrain_options)
        self.frontier_proposal_carousel.valueChanged.connect(
            self.frontier_proposal_changed.emit
        )
        self.frontier_proposal_carousel.valueChanged.connect(
            self._update_frontier_proposal_label
        )
        layout.addWidget(self.frontier_proposal_label, 1, 0)
        layout.addWidget(self.frontier_proposal_carousel, 1, 1)

    def get_home_terrain(self) -> Optional[str]:
        return self.home_terrain_carousel.value()

    def set_home_terrain(self, terrain_name: Optional[str]):
        self.home_terrain_carousel.setValue(terrain_name)

    def get_frontier_proposal(self) -> Optional[str]:
        return self.frontier_proposal_carousel.value()

    def set_frontier_proposal(self, terrain_name: Optional[str]):
        self.frontier_proposal_carousel.setValue(terrain_name)

    def clear_selections(self):
        if self.all_terrain_options:
            self.home_terrain_carousel.setValue(self.all_terrain_options[0])
            self.frontier_proposal_carousel.setValue(self.all_terrain_options[0])
            # Update labels with the first terrain option
            self._update_home_terrain_label(self.all_terrain_options[0])
            self._update_frontier_proposal_label(self.all_terrain_options[0])

    def _update_home_terrain_label(self, terrain_name: str):
        """Keep home terrain label static - terrain name only shows in carousel."""
        # Label should always show just the static text, not the terrain name
        self.home_terrain_label.setText("🏠 Home Terrain:")

    def _update_frontier_proposal_label(self, terrain_name: str):
        """Keep frontier proposal label static - terrain name only shows in carousel."""
        # Label should always show just the static text, not the terrain name
        self.frontier_proposal_label.setText("🗺️ Proposed Frontier Terrain:")
