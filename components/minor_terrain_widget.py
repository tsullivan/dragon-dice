"""
Minor Terrain Management Widget for Dragon Dice.

This widget provides a comprehensive interface for managing minor terrain
placements, face settings, and effects visualization during gameplay.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .carousel import CarouselInputWidget
from models.minor_terrain_model import MinorTerrain, get_all_minor_terrain_objects, get_minor_terrain
from models.element_model import get_element_icon


class MinorTerrainDisplayItem(QFrame):
    """Individual minor terrain display item showing current face and effects."""

    face_change_requested = Signal(str, str, int)  # terrain_name, minor_terrain_name, new_face_index
    removal_requested = Signal(str, str)  # terrain_name, minor_terrain_name
    burial_requested = Signal(str, str)  # terrain_name, minor_terrain_name

    def __init__(self, placement_data: Dict[str, Any], minor_terrain: MinorTerrain, parent=None):
        super().__init__(parent)
        self.placement_data = placement_data
        self.minor_terrain = minor_terrain
        self.major_terrain_name = placement_data.get("major_terrain_name", "Unknown")
        self.current_face_index = placement_data.get("current_face_index", 0)
        self.controlling_player = placement_data.get("controlling_player", "Unknown")
        self.needs_burial = placement_data.get("needs_burial", False)

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)

        # Apply styling based on burial state
        self._update_styling()
        self._setup_ui()

    def _update_styling(self):
        """Update styling based on terrain state."""
        if self.needs_burial:
            # Red/dark styling for burial state
            style = """
                MinorTerrainDisplayItem {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #8B0000, stop:1 #2a0000);
                    border: 2px solid #FF6B6B;
                    border-radius: 8px;
                    margin: 2px;
                }
                MinorTerrainDisplayItem:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #A00000, stop:1 #4a0000);
                    border-color: #FF8B8B;
                }
            """
        else:
            # Normal green/earth styling
            style = """
                MinorTerrainDisplayItem {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #228B22, stop:1 #006400);
                    border: 2px solid #90EE90;
                    border-radius: 8px;
                    margin: 2px;
                }
                MinorTerrainDisplayItem:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #32CD32, stop:1 #008000);
                    border-color: #98FB98;
                }
            """
        self.setStyleSheet(style)

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        # Header with terrain name and elements
        header_layout = QHBoxLayout()

        # Terrain name with element icons
        elements_text = "".join(get_element_icon(elem) for elem in self.minor_terrain.elements)
        name_label = QLabel(f"{elements_text} {self.minor_terrain.name}")
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        # Controller info
        controller_label = QLabel(f"👤 {self.controlling_player}")
        controller_label.setStyleSheet("color: #FFD700; font-size: 10px;")
        header_layout.addWidget(controller_label)

        layout.addLayout(header_layout)

        # Current face display and controls
        face_layout = QHBoxLayout()

        # Current face info
        current_face = self.minor_terrain.faces[self.current_face_index]
        face_info_layout = QVBoxLayout()

        face_name_label = QLabel(f"⚡ {current_face.name}")
        face_name_label.setStyleSheet("color: #87CEEB; font-weight: bold; font-size: 10px;")
        face_info_layout.addWidget(face_name_label)

        # Truncate description if too long
        description = current_face.description
        if len(description) > 60:
            description = description[:57] + "..."
        face_desc_label = QLabel(description)
        face_desc_label.setStyleSheet("color: #F0F8FF; font-size: 9px;")
        face_desc_label.setWordWrap(True)
        face_info_layout.addWidget(face_desc_label)

        face_layout.addLayout(face_info_layout)

        # Face selection carousel
        face_names = [face.name for face in self.minor_terrain.faces]
        self.face_carousel = CarouselInputWidget(allowed_values=face_names, initial_value=current_face.name)
        self.face_carousel.value_changed.connect(self._on_face_changed)
        self.face_carousel.setMaximumWidth(120)
        face_layout.addWidget(self.face_carousel)

        layout.addLayout(face_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        # Remove button
        remove_btn = QPushButton("❌")
        remove_btn.setToolTip("Remove minor terrain")
        remove_btn.setStyleSheet(self._get_button_style("#8B4513"))
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(self._on_remove_requested)
        button_layout.addWidget(remove_btn)

        # Bury button (only if needs burial)
        if self.needs_burial:
            bury_btn = QPushButton("⚰️")
            bury_btn.setToolTip("Bury minor terrain")
            bury_btn.setStyleSheet(self._get_button_style("#8B0000"))
            bury_btn.setMaximumWidth(30)
            bury_btn.clicked.connect(self._on_burial_requested)
            button_layout.addWidget(bury_btn)

        button_layout.addStretch()

        # Major terrain location
        location_label = QLabel(f"📍 {self.major_terrain_name}")
        location_label.setStyleSheet("color: #DDA0DD; font-size: 9px;")
        button_layout.addWidget(location_label)

        layout.addLayout(button_layout)

    def _get_button_style(self, color: str) -> str:
        """Get button styling."""
        return f"""
            QPushButton {{
                background: {color};
                border: 1px solid white;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-height: 20px;
                max-height: 20px;
            }}
            QPushButton:hover {{
                background: {color}AA;
            }}
            QPushButton:pressed {{
                background: {color}66;
            }}
        """

    def _on_face_changed(self, face_name: str):
        """Handle face change from carousel."""
        if face_name:
            # Find face index
            for i, face in enumerate(self.minor_terrain.faces):
                if face.name == face_name:
                    self.face_change_requested.emit(self.major_terrain_name, self.minor_terrain.name, i)
                    break

    def _on_remove_requested(self):
        """Handle removal request."""
        self.removal_requested.emit(self.major_terrain_name, self.minor_terrain.name)

    def _on_burial_requested(self):
        """Handle burial request."""
        self.burial_requested.emit(self.major_terrain_name, self.minor_terrain.name)

    def update_face_display(self, new_face_index: int, needs_burial: bool = False):
        """Update the face display and burial state."""
        self.current_face_index = new_face_index
        self.needs_burial = needs_burial
        self._update_styling()

        # Update face carousel
        current_face = self.minor_terrain.faces[self.current_face_index]
        self.face_carousel.set_value(current_face.name)


class MinorTerrainPlacementDialog(QFrame):
    """Dialog for placing new minor terrains."""

    placement_requested = Signal(str, str, str)  # minor_terrain_key, major_terrain_name, controlling_player

    def __init__(self, available_terrains: List[str], available_players: List[str], parent=None):
        super().__init__(parent)
        self.available_terrains = available_terrains
        self.available_players = available_players

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(2)
        self.setStyleSheet("""
            MinorTerrainPlacementDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4A5D23, stop:1 #2F3E15);
                border: 2px solid #90EE90;
                border-radius: 8px;
                margin: 2px;
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the placement dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Title
        title_label = QLabel("🏔️ Place Minor Terrain")
        title_label.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 12px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Minor terrain selection
        terrain_layout = QHBoxLayout()
        terrain_layout.addWidget(QLabel("Terrain:"))

        # Get all minor terrain options with nice display names
        minor_terrain_options = []
        for terrain in get_all_minor_terrain_objects():
            elements_text = "".join(get_element_icon(elem) for elem in terrain.elements)
            display_name = f"{elements_text} {terrain.name}"
            # Create key from base name and eighth face
            terrain_base = terrain.get_terrain_base_name().upper()
            terrain_key = f"{terrain_base}_{terrain.eighth_face.upper()}"
            minor_terrain_options.append((display_name, terrain_key))

        self.terrain_carousel = CarouselInputWidget(allowed_values=[option[0] for option in minor_terrain_options])
        self.terrain_carousel.setMinimumWidth(200)
        terrain_layout.addWidget(self.terrain_carousel)
        layout.addLayout(terrain_layout)

        # Major terrain selection
        major_terrain_layout = QHBoxLayout()
        major_terrain_layout.addWidget(QLabel("Location:"))

        self.location_carousel = CarouselInputWidget(allowed_values=self.available_terrains)
        self.location_carousel.setMinimumWidth(150)
        major_terrain_layout.addWidget(self.location_carousel)
        layout.addLayout(major_terrain_layout)

        # Player selection
        player_layout = QHBoxLayout()
        player_layout.addWidget(QLabel("Controller:"))

        self.player_carousel = CarouselInputWidget(allowed_values=self.available_players)
        self.player_carousel.setMinimumWidth(120)
        player_layout.addWidget(self.player_carousel)
        layout.addLayout(player_layout)

        # Place button
        place_btn = QPushButton("🏔️ Place Terrain")
        place_btn.setStyleSheet("""
            QPushButton {
                background: #228B22;
                border: 1px solid #90EE90;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: #32CD32;
            }
            QPushButton:pressed {
                background: #006400;
            }
        """)
        place_btn.clicked.connect(self._on_place_requested)
        layout.addWidget(place_btn)

        # Store terrain mapping for lookup
        self.terrain_mapping = {option[0]: option[1] for option in minor_terrain_options}

    def _on_place_requested(self):
        """Handle placement request."""
        terrain_display = self.terrain_carousel.value()
        location = self.location_carousel.value()
        player = self.player_carousel.value()

        if terrain_display and location and player:
            # Get terrain key from mapping
            terrain_key = self.terrain_mapping.get(terrain_display, terrain_display)
            if terrain_key:
                self.placement_requested.emit(terrain_key, location, player)


class MinorTerrainWidget(QGroupBox):
    """Main widget for managing minor terrain placements and effects."""

    placement_requested = Signal(str, str, str)  # minor_terrain_key, major_terrain_name, controlling_player
    face_change_requested = Signal(str, str, int)  # terrain_name, minor_terrain_name, new_face_index
    removal_requested = Signal(str, str)  # terrain_name, minor_terrain_name
    burial_requested = Signal(str, str)  # terrain_name, minor_terrain_name
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("🏔️ Minor Terrain Management", parent)
        self.setMinimumWidth(350)
        self.setMinimumHeight(300)

        # Apply styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: white;
                border: 3px solid #90EE90;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #228B22, stop:1 #006400);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #FFD700;
                font-size: 16px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            }
        """)

        self.placement_items: List[MinorTerrainDisplayItem] = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the main widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(8)

        # Header with statistics and refresh
        header_layout = QHBoxLayout()

        self.stats_label = QLabel("Minor Terrains: 0")
        self.stats_label.setStyleSheet("""
            color: #90EE90;
            font-size: 12px;
            font-weight: normal;
        """)
        header_layout.addWidget(self.stats_label)

        header_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #228B22;
                border: 1px solid #90EE90;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-width: 30px;
                max-width: 30px;
                min-height: 25px;
                max-height: 25px;
            }
            QPushButton:hover {
                background: #32CD32;
            }
            QPushButton:pressed {
                background: #006400;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Placement dialog (initially hidden)
        self.placement_dialog = None

        # Add placement button
        add_btn = QPushButton("➕ Add Minor Terrain")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #228B22;
                border: 1px solid #90EE90;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: #32CD32;
            }
            QPushButton:pressed {
                background: #006400;
            }
        """)
        add_btn.clicked.connect(self._show_placement_dialog)
        layout.addWidget(add_btn)

        # Scrollable terrain list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #2a4a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #90EE90;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #98FB98;
            }
        """)

        # Container for minor terrain items
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)

        # Empty state label
        self.empty_label = QLabel("No minor terrains placed")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            color: #90EE90;
            font-style: italic;
            font-size: 12px;
            padding: 20px;
        """)
        self.content_layout.addWidget(self.empty_label)

        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)

    def _show_placement_dialog(self):
        """Show the placement dialog."""
        # This would need to be connected to get current terrain and player data
        # For now, use placeholder data
        available_terrains = ["Highland", "Coastland", "Frontier", "Deadland"]
        available_players = ["Player 1", "Player 2"]

        if self.placement_dialog:
            self.placement_dialog.deleteLater()

        self.placement_dialog = MinorTerrainPlacementDialog(available_terrains, available_players)
        self.placement_dialog.placement_requested.connect(self.placement_requested.emit)

        # Insert at the top of the content area
        self.content_layout.insertWidget(0, self.placement_dialog)

    def update_placements(self, placements_data: Dict[str, List[Dict[str, Any]]]):
        """Update the display with current placement data.

        Args:
            placements_data: Dictionary mapping terrain names to placement lists
        """
        # Clear existing items
        for item in self.placement_items:
            item.deleteLater()
        self.placement_items.clear()

        # Clear content layout (except empty label)
        while self.content_layout.count() > 0:
            child = self.content_layout.takeAt(0)
            if child.widget() and child.widget() != self.empty_label:
                child.widget().deleteLater()

        total_placements = 0

        # Add terrain sections
        for terrain_name, placements in placements_data.items():
            if not placements:
                continue

            # Terrain section header
            terrain_header = QLabel(f"📍 {terrain_name}")
            terrain_header.setStyleSheet("""
                QLabel {
                    color: #FFD700;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 4px 8px;
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 4px;
                    margin: 4px 0px 2px 0px;
                }
            """)
            self.content_layout.addWidget(terrain_header)

            # Add placement items
            for placement_data in placements:
                # Get minor terrain object using base name and eighth face
                terrain_base_name = placement_data.get("terrain_base_name", "").upper()
                eighth_face = placement_data.get("eighth_face", "").upper()
                terrain_name_key = f"{terrain_base_name}_{eighth_face}"

                minor_terrain = get_minor_terrain(terrain_name_key)
                if minor_terrain:
                    item = MinorTerrainDisplayItem(placement_data, minor_terrain)
                    item.face_change_requested.connect(self.face_change_requested.emit)
                    item.removal_requested.connect(self.removal_requested.emit)
                    item.burial_requested.connect(self.burial_requested.emit)

                    self.content_layout.addWidget(item)
                    self.placement_items.append(item)
                    total_placements += 1

        # Update statistics
        self.stats_label.setText(f"Minor Terrains: {total_placements}")

        # Show empty state if no placements
        if total_placements == 0:
            self.content_layout.addWidget(self.empty_label)
        else:
            # Remove empty label if it exists
            if self.empty_label.parent():
                self.content_layout.removeWidget(self.empty_label)

        # Add stretch to push content to top
        self.content_layout.addStretch()

    def highlight_terrain_placements(self, terrain_name: str):
        """Highlight placements for a specific terrain."""
        # Could be implemented to show visual emphasis
        pass

    def get_placement_count(self) -> int:
        """Get total number of minor terrain placements."""
        return len(self.placement_items)

    def update_available_options(self, available_terrains: List[str], available_players: List[str]):
        """Update available options for placement dialog."""
        # This would update the placement dialog options when terrain/player state changes
        pass
