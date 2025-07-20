"""
Minor Terrain Management Dialog for Dragon Dice.

This dialog provides interfaces for:
1. Placing minor terrains on major terrains
2. Setting minor terrain faces
3. Managing minor terrain effects
4. Processing burial requirements
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from components.carousel import CarouselInputWidget
from models.element_model import get_element_icon
from models.minor_terrain_model import MinorTerrain, get_all_minor_terrain_objects, get_minor_terrain


class MinorTerrainFaceSelector(QGroupBox):
    """Widget for selecting minor terrain faces with visual feedback."""

    face_selected = Signal(int, str)  # face_index, face_name

    def __init__(self, minor_terrain: MinorTerrain, current_face_index: int = 0, parent=None):
        super().__init__(f"🎲 {minor_terrain.name} Face Selection", parent)
        self.minor_terrain = minor_terrain
        self.current_face_index = current_face_index

        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: white;
                border: 2px solid #90EE90;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2F5233, stop:1 #1a3020);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px 0 6px;
                color: #FFD700;
                font-size: 13px;
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the face selector UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 8)

        # Elements display
        elements_layout = QHBoxLayout()
        elements_text = "".join(get_element_icon(elem) for elem in self.minor_terrain.elements)
        elements_label = QLabel(f"Elements: {elements_text}")
        elements_label.setStyleSheet("color: #87CEEB; font-size: 11px;")
        elements_layout.addWidget(elements_label)
        elements_layout.addStretch()
        layout.addLayout(elements_layout)

        # Current face display
        current_face = self.minor_terrain.faces[self.current_face_index]
        self.current_face_label = QLabel(f"Current: {current_face.name}")
        self.current_face_label.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.current_face_label)

        # Face description
        self.face_description = QLabel(current_face.description)
        self.face_description.setStyleSheet("color: #F0F8FF; font-size: 10px; margin: 4px;")
        self.face_description.setWordWrap(True)
        layout.addWidget(self.face_description)

        # Face selection carousel
        face_layout = QHBoxLayout()
        face_layout.addWidget(QLabel("Select Face:"))

        face_names = [f"{i + 1}. {face.name}" for i, face in enumerate(self.minor_terrain.faces)]
        self.face_carousel = CarouselInputWidget(
            allowed_values=face_names, initial_value=f"{self.current_face_index + 1}. {current_face.name}"
        )
        self.face_carousel.value_changed.connect(self._on_face_changed)
        face_layout.addWidget(self.face_carousel)

        layout.addLayout(face_layout)

        # Effect preview
        self.effect_preview = QLabel()
        self.effect_preview.setStyleSheet("color: #DDA0DD; font-size: 10px; font-style: italic;")
        self.effect_preview.setWordWrap(True)
        layout.addWidget(self.effect_preview)

        self._update_effect_preview()

    def _on_face_changed(self, face_display: str):
        """Handle face change from carousel."""
        if face_display:
            # Extract face index from display format "1. Face Name"
            try:
                face_index = int(face_display.split(".")[0]) - 1
                if 0 <= face_index < len(self.minor_terrain.faces):
                    self.current_face_index = face_index
                    face = self.minor_terrain.faces[face_index]

                    # Update displays
                    self.current_face_label.setText(f"Current: {face.name}")
                    self.face_description.setText(face.description)
                    self._update_effect_preview()

                    # Emit signal
                    self.face_selected.emit(face_index, face.name)
            except (ValueError, IndexError):
                pass

    def _update_effect_preview(self):
        """Update the effect preview based on current face."""
        face = self.minor_terrain.faces[self.current_face_index]
        face_name = face.name

        # Categorize effect
        if face_name == "ID":
            effect_text = "⚡ Choice Effect: Player can select any action face"
        elif face_name in ["Magic", "Melee", "Missile"]:
            effect_text = f"🎯 Action Effect: Enables {face_name} action"
        elif face_name in ["Double Saves", "Double Maneuvers"]:
            effect_text = f"⬆️ Enhancement: {face_name} for controlling army"
        elif face_name in ["Flood", "Flanked", "Landslide", "Revolt"]:
            effect_text = f"⚠️ Negative Effect: {face_name} - Terrain will be buried!"
        else:
            effect_text = "❓ Unknown effect type"

        self.effect_preview.setText(effect_text)

    def get_selected_face_index(self) -> int:
        """Get the currently selected face index."""
        return self.current_face_index


class MinorTerrainPlacementSelector(QGroupBox):
    """Widget for selecting where to place a minor terrain."""

    placement_configured = Signal(str, str, str)  # terrain_key, location, controller

    def __init__(self, available_locations: List[str], available_players: List[str], parent=None):
        super().__init__("🏔️ Minor Terrain Placement", parent)
        self.available_locations = available_locations
        self.available_players = available_players

        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: white;
                border: 2px solid #90EE90;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2F5233, stop:1 #1a3020);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px 0 6px;
                color: #FFD700;
                font-size: 13px;
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the placement selector UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 8)

        # Terrain type selection
        terrain_layout = QHBoxLayout()
        terrain_layout.addWidget(QLabel("Terrain Type:"))

        # Create display options for minor terrains
        terrain_options = []
        self.terrain_mapping = {}

        for terrain in get_all_minor_terrain_objects():
            elements_text = "".join(get_element_icon(elem) for elem in terrain.elements)
            display_name = f"{elements_text} {terrain.name}"
            terrain_options.append(display_name)

            # Create mapping key using base name and eighth face
            terrain_base = terrain.get_terrain_base_name().upper()
            terrain_key = f"{terrain_base}_{terrain.eighth_face.upper()}"
            self.terrain_mapping[display_name] = terrain_key

        self.terrain_carousel = CarouselInputWidget(allowed_values=terrain_options)
        self.terrain_carousel.value_changed.connect(self._on_selection_changed)
        terrain_layout.addWidget(self.terrain_carousel)
        layout.addLayout(terrain_layout)

        # Location selection
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Location:"))

        self.location_carousel = CarouselInputWidget(allowed_values=self.available_locations)
        self.location_carousel.value_changed.connect(self._on_selection_changed)
        location_layout.addWidget(self.location_carousel)
        layout.addLayout(location_layout)

        # Controller selection
        controller_layout = QHBoxLayout()
        controller_layout.addWidget(QLabel("Controller:"))

        self.controller_carousel = CarouselInputWidget(allowed_values=self.available_players)
        self.controller_carousel.value_changed.connect(self._on_selection_changed)
        controller_layout.addWidget(self.controller_carousel)
        layout.addLayout(controller_layout)

        # Preview
        self.preview_label = QLabel("Select options to preview placement")
        self.preview_label.setStyleSheet("color: #DDA0DD; font-size: 10px; font-style: italic;")
        self.preview_label.setWordWrap(True)
        layout.addWidget(self.preview_label)

    def _on_selection_changed(self, _):
        """Handle selection changes."""
        terrain_display = self.terrain_carousel.value()
        location = self.location_carousel.value()
        controller = self.controller_carousel.value()

        if terrain_display and location and controller:
            terrain_key = self.terrain_mapping.get(terrain_display, "")
            self.preview_label.setText(f"📋 Will place {terrain_display} at {location} controlled by {controller}")
            self.placement_configured.emit(terrain_key, location, controller)
        else:
            self.preview_label.setText("Select options to preview placement")

    def get_current_selection(self) -> Optional[tuple]:
        """Get current selection as (terrain_key, location, controller)."""
        terrain_display = self.terrain_carousel.value()
        location = self.location_carousel.value()
        controller = self.controller_carousel.value()

        if terrain_display and location and controller:
            terrain_key = self.terrain_mapping.get(terrain_display, "")
            return (terrain_key, location, controller)
        return None


class MinorTerrainManagementDialog(QDialog):
    """Comprehensive dialog for minor terrain management."""

    terrain_placed = Signal(str, str, str)  # terrain_key, location, controller
    face_changed = Signal(str, str, int)  # location, terrain_name, face_index
    terrain_removed = Signal(str, str)  # location, terrain_name
    terrain_buried = Signal(str, str)  # location, terrain_name

    def __init__(
        self,
        available_locations: List[str],
        available_players: List[str],
        current_placements: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.available_locations = available_locations
        self.available_players = available_players
        self.current_placements = current_placements or {}

        self.setWindowTitle("Minor Terrain Management")
        self.setMinimumSize(500, 600)
        self.setModal(True)

        # Apply dialog styling
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a3a1a, stop:1 #0d2a0d);
                color: white;
            }
            QTabWidget::pane {
                border: 2px solid #90EE90;
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.2);
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: #228B22;
                color: white;
                padding: 8px 16px;
                margin: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #32CD32;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #2E8B57;
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("🏔️ Minor Terrain Management")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FFD700;
            text-align: center;
            margin: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Tab widget for different functions
        self.tab_widget = QTabWidget()

        # Placement tab
        self.placement_tab = self._create_placement_tab()
        self.tab_widget.addTab(self.placement_tab, "📍 Place Terrain")

        # Management tab
        self.management_tab = self._create_management_tab()
        self.tab_widget.addTab(self.management_tab, "⚙️ Manage Existing")

        # Effects tab
        self.effects_tab = self._create_effects_tab()
        self.tab_widget.addTab(self.effects_tab, "✨ View Effects")

        layout.addWidget(self.tab_widget)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.setStyleSheet("""
            QDialogButtonBox QPushButton {
                background: #228B22;
                border: 1px solid #90EE90;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background: #32CD32;
            }
            QDialogButtonBox QPushButton:pressed {
                background: #006400;
            }
        """)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

    def _create_placement_tab(self) -> QWidget:
        """Create the placement tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Placement selector
        self.placement_selector = MinorTerrainPlacementSelector(self.available_locations, self.available_players)
        layout.addWidget(self.placement_selector)

        # Place button
        place_btn = QPushButton("🏔️ Place Minor Terrain")
        place_btn.setStyleSheet("""
            QPushButton {
                background: #228B22;
                border: 1px solid #90EE90;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #32CD32;
            }
            QPushButton:pressed {
                background: #006400;
            }
            QPushButton:disabled {
                background: #666666;
                color: #999999;
            }
        """)
        place_btn.clicked.connect(self._on_place_terrain)
        layout.addWidget(place_btn)

        layout.addStretch()
        return tab

    def _create_management_tab(self) -> QWidget:
        """Create the management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Scroll area for current placements
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #90EE90;
                border-radius: 4px;
                background: transparent;
            }
        """)

        self.placements_container = QWidget()
        self.placements_layout = QVBoxLayout(self.placements_container)
        self.placements_layout.setContentsMargins(5, 5, 5, 5)

        scroll_area.setWidget(self.placements_container)
        layout.addWidget(scroll_area)

        # Refresh placements display
        self._refresh_placements_display()

        return tab

    def _create_effects_tab(self) -> QWidget:
        """Create the effects overview tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Effects summary
        effects_label = QLabel("📊 Current Minor Terrain Effects")
        effects_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFD700; margin: 5px;")
        layout.addWidget(effects_label)

        # Scroll area for effects
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #90EE90;
                border-radius: 4px;
                background: transparent;
            }
        """)

        self.effects_container = QWidget()
        self.effects_layout = QVBoxLayout(self.effects_container)
        self.effects_layout.setContentsMargins(5, 5, 5, 5)

        scroll_area.setWidget(self.effects_container)
        layout.addWidget(scroll_area)

        # Refresh effects display
        self._refresh_effects_display()

        return tab

    def _refresh_placements_display(self):
        """Refresh the display of current placements."""
        # Clear existing content
        while self.placements_layout.count():
            child = self.placements_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.current_placements:
            empty_label = QLabel("No minor terrains currently placed")
            empty_label.setStyleSheet("color: #90EE90; font-style: italic; text-align: center; margin: 20px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.placements_layout.addWidget(empty_label)
            return

        # Add terrain sections
        for location, placements in self.current_placements.items():
            if not placements:
                continue

            # Location header
            location_header = QLabel(f"📍 {location}")
            location_header.setStyleSheet("""
                font-size: 13px;
                font-weight: bold;
                color: #FFD700;
                background: rgba(0, 0, 0, 0.3);
                padding: 4px 8px;
                border-radius: 4px;
                margin: 4px 0px 2px 0px;
            """)
            self.placements_layout.addWidget(location_header)

            # Add each placement
            for placement_data in placements:
                placement_widget = self._create_placement_widget(location, placement_data)
                self.placements_layout.addWidget(placement_widget)

        self.placements_layout.addStretch()

    def _create_placement_widget(self, location: str, placement_data: Dict[str, Any]) -> QWidget:
        """Create a widget for a single placement."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background: rgba(34, 139, 34, 0.3);
                border: 1px solid #90EE90;
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
            }
        """)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)

        # Terrain info
        terrain_name = placement_data.get("minor_terrain_name", "Unknown")
        controller = placement_data.get("controlling_player", "Unknown")
        face_index = placement_data.get("current_face_index", 0)
        needs_burial = placement_data.get("needs_burial", False)

        # Get terrain object for face info using base name and eighth face
        terrain_base_name = placement_data.get("terrain_base_name", "").upper()
        eighth_face = placement_data.get("eighth_face", "").upper()
        terrain_key = f"{terrain_base_name}_{eighth_face}"
        terrain = get_minor_terrain(terrain_key)

        info_layout = QVBoxLayout()

        # Terrain name and controller
        name_label = QLabel(f"🏔️ {terrain_name} (👤 {controller})")
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        info_layout.addWidget(name_label)

        # Current face
        if terrain and 0 <= face_index < len(terrain.faces):
            face_name = terrain.faces[face_index].name
            if needs_burial:
                face_label = QLabel(f"⚠️ Face: {face_name} (NEEDS BURIAL)")
                face_label.setStyleSheet("color: #FF6B6B; font-size: 10px;")
            else:
                face_label = QLabel(f"⚡ Face: {face_name}")
                face_label.setStyleSheet("color: #87CEEB; font-size: 10px;")
            info_layout.addWidget(face_label)

        layout.addLayout(info_layout)

        # Action buttons
        button_layout = QVBoxLayout()

        # Face selection button (if terrain exists)
        if terrain:
            face_btn = QPushButton("🎲")
            face_btn.setToolTip("Change face")
            face_btn.setMaximumWidth(30)
            face_btn.setStyleSheet(self._get_button_style("#4169E1"))
            face_btn.clicked.connect(lambda: self._show_face_selector(location, terrain, face_index))
            button_layout.addWidget(face_btn)

        # Remove button
        remove_btn = QPushButton("❌")
        remove_btn.setToolTip("Remove terrain")
        remove_btn.setMaximumWidth(30)
        remove_btn.setStyleSheet(self._get_button_style("#8B4513"))
        remove_btn.clicked.connect(lambda: self._remove_terrain(location, terrain_name))
        button_layout.addWidget(remove_btn)

        # Bury button (if needs burial)
        if needs_burial:
            bury_btn = QPushButton("⚰️")
            bury_btn.setToolTip("Bury terrain")
            bury_btn.setMaximumWidth(30)
            bury_btn.setStyleSheet(self._get_button_style("#8B0000"))
            bury_btn.clicked.connect(lambda: self._bury_terrain(location, terrain_name))
            button_layout.addWidget(bury_btn)

        layout.addLayout(button_layout)

        return widget

    def _get_button_style(self, color: str) -> str:
        """Get button styling."""
        return f"""
            QPushButton {{
                background: {color};
                border: 1px solid white;
                border-radius: 3px;
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

    def _refresh_effects_display(self):
        """Refresh the effects display."""
        # Clear existing content
        while self.effects_layout.count():
            child = self.effects_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.current_placements:
            empty_label = QLabel("No minor terrain effects currently active")
            empty_label.setStyleSheet("color: #90EE90; font-style: italic; text-align: center; margin: 20px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.effects_layout.addWidget(empty_label)
            return

        # Summarize effects by type
        effects_summary: Dict[str, List] = {"action": [], "enhancement": [], "choice": [], "negative": []}

        for location, placements in self.current_placements.items():
            for placement_data in placements:
                terrain_base_name = placement_data.get("terrain_base_name", "").upper()
                eighth_face = placement_data.get("eighth_face", "").upper()
                terrain_key = f"{terrain_base_name}_{eighth_face}"
                terrain = get_minor_terrain(terrain_key)
                if terrain:
                    face_index = placement_data.get("current_face_index", 0)
                    if 0 <= face_index < len(terrain.faces):
                        face = terrain.faces[face_index]
                        controller = placement_data.get("controlling_player", "Unknown")

                        effect_info = {
                            "terrain": terrain.name,
                            "location": location,
                            "controller": controller,
                            "face": face.name,
                            "description": face.description,
                        }

                        # Categorize effect
                        if face.name == "ID":
                            effects_summary["choice"].append(effect_info)
                        elif face.name in ["Magic", "Melee", "Missile"]:
                            effects_summary["action"].append(effect_info)
                        elif face.name in ["Double Saves", "Double Maneuvers"]:
                            effects_summary["enhancement"].append(effect_info)
                        elif face.name in ["Flood", "Flanked", "Landslide", "Revolt"]:
                            effects_summary["negative"].append(effect_info)

        # Display effects by category
        categories = [
            ("choice", "⚡ Choice Effects", "#FFD700"),
            ("action", "🎯 Action Effects", "#87CEEB"),
            ("enhancement", "⬆️ Enhancement Effects", "#90EE90"),
            ("negative", "⚠️ Negative Effects", "#FF6B6B"),
        ]

        for category, title, color in categories:
            effects = effects_summary[category]
            if effects:
                # Category header
                header = QLabel(title)
                header.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {color}; margin: 5px 0px 2px 0px;")
                self.effects_layout.addWidget(header)

                # Effects list
                for effect in effects:
                    effect_widget = self._create_effect_widget(effect, color)
                    self.effects_layout.addWidget(effect_widget)

        self.effects_layout.addStretch()

    def _create_effect_widget(self, effect_info: Dict[str, Any], color: str) -> QWidget:
        """Create a widget for an effect summary."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet(f"""
            QFrame {{
                background: rgba(0, 0, 0, 0.2);
                border: 1px solid {color};
                border-radius: 3px;
                margin: 1px;
                padding: 2px;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 3, 6, 3)

        # Header line
        header = QLabel(f"🏔️ {effect_info['terrain']} at {effect_info['location']} (👤 {effect_info['controller']})")
        header.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
        layout.addWidget(header)

        # Effect description
        desc = QLabel(f"⚡ {effect_info['face']}: {effect_info['description']}")
        desc.setStyleSheet(f"color: {color}; font-size: 9px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        return widget

    def _show_face_selector(self, location: str, terrain: MinorTerrain, current_face_index: int):
        """Show face selector for a terrain."""
        # Create a mini-dialog for face selection
        face_dialog = QDialog(self)
        face_dialog.setWindowTitle(f"Set {terrain.name} Face")
        face_dialog.setModal(True)
        face_dialog.setMinimumSize(300, 200)

        layout = QVBoxLayout(face_dialog)

        face_selector = MinorTerrainFaceSelector(terrain, current_face_index)
        layout.addWidget(face_selector)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        def on_accepted():
            new_face_index = face_selector.get_selected_face_index()
            self.face_changed.emit(location, terrain.name, new_face_index)
            face_dialog.accept()

        button_box.accepted.connect(on_accepted)
        button_box.rejected.connect(face_dialog.reject)
        layout.addWidget(button_box)

        face_dialog.exec()

    def _remove_terrain(self, location: str, terrain_name: str):
        """Remove a terrain."""
        self.terrain_removed.emit(location, terrain_name)

    def _bury_terrain(self, location: str, terrain_name: str):
        """Bury a terrain."""
        self.terrain_buried.emit(location, terrain_name)

    def _on_place_terrain(self):
        """Handle placing a new terrain."""
        selection = self.placement_selector.get_current_selection()
        if selection:
            terrain_key, location, controller = selection
            self.terrain_placed.emit(terrain_key, location, controller)

    def update_placements(self, placements_data: Dict[str, List[Dict[str, Any]]]):
        """Update the dialog with new placement data."""
        self.current_placements = placements_data
        self._refresh_placements_display()
        self._refresh_effects_display()
