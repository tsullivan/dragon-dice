# components/terrain_selection_widget.py
from typing import List, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

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
        self.frontier_proposal_carousel.valueChanged.connect(self.frontier_proposal_changed.emit)
        self.frontier_proposal_carousel.valueChanged.connect(self._update_frontier_proposal_label)
        layout.addWidget(self.frontier_proposal_label, 1, 0)
        layout.addWidget(self.frontier_proposal_carousel, 1, 1)

    def get_home_terrain(self) -> Optional[str]:
        value = self.home_terrain_carousel.value()
        return self._extract_terrain_name(str(value)) if value else None

    def set_home_terrain(self, terrain_name: Optional[str]):
        if terrain_name:
            formatted_value = self._find_formatted_terrain(terrain_name)
            self.home_terrain_carousel.setValue(formatted_value)
        else:
            self.home_terrain_carousel.setValue(None)

    def get_frontier_proposal(self) -> Optional[str]:
        value = self.frontier_proposal_carousel.value()
        return self._extract_terrain_name(str(value)) if value else None

    def set_frontier_proposal(self, terrain_name: Optional[str]):
        if terrain_name:
            formatted_value = self._find_formatted_terrain(terrain_name)
            self.frontier_proposal_carousel.setValue(formatted_value)
        else:
            self.frontier_proposal_carousel.setValue(None)

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

    def _extract_terrain_name(self, formatted_value: str) -> str:
        """Extract terrain name from formatted display like '🟦🟩 Coastland Castle' -> 'Coastland Castle'."""
        # Split on spaces and skip emoji characters (which are typically single "words")
        parts = formatted_value.split()
        # Filter out parts that contain emoji (typically the element color icons)
        text_parts = [part for part in parts if not any(ord(char) > 127 for char in part)]
        return " ".join(text_parts) if text_parts else formatted_value

    def _find_formatted_terrain(self, terrain_name: str) -> Optional[str]:
        """Find the formatted terrain option that contains the given terrain name."""
        for option in self.all_terrain_options:
            if terrain_name in option:
                return option
        return terrain_name  # Fallback to original name if not found
