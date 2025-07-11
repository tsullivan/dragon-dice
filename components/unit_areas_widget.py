"""
Unit Areas Widget for Dragon Dice - DUA and BUA.

This widget displays the Dead Unit Area (DUA) and Buried Unit Area (BUA)
for all players, showing units that have been killed or buried.
Based on the design from assets/playmat.html.
"""

from typing import Any, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class UnitAreaItem(QFrame):
    """Individual unit display item for DUA/BUA."""

    unit_selected = Signal(dict)  # Emit unit data when clicked

    def __init__(self, unit_data: Dict[str, Any], area_type: str = "DUA", parent=None):
        super().__init__(parent)
        self.unit_data = unit_data
        self.area_type = area_type
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        self.setMinimumHeight(45)
        self.setMaximumHeight(65)

        # Apply different styling based on area type
        if area_type == "DUA":
            # Dark red gradient for dead units
            self.setStyleSheet("""
                UnitAreaItem {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #8b0000, stop:1 #4b0000);
                    border: 2px solid #ff6b6b;
                    border-radius: 6px;
                    margin: 1px;
                }
                UnitAreaItem:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #ab0000, stop:1 #6b0000);
                    border-color: #ff8b8b;
                }
            """)
        else:  # BUA
            # Dark gray gradient for buried units
            self.setStyleSheet("""
                UnitAreaItem {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2f2f2f, stop:1 #1a1a1a);
                    border: 2px solid #696969;
                    border-radius: 6px;
                    margin: 1px;
                }
                UnitAreaItem:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #4f4f4f, stop:1 #3a3a3a);
                    border-color: #898989;
                }
            """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)

        # Unit info
        unit_info = QVBoxLayout()

        # Unit name and species
        name = unit_data.get("name", "Unknown Unit")
        species = unit_data.get("species", "Unknown")
        name_label = QLabel(f"💀 {name}" if area_type == "DUA" else f"⚱️ {name}")
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 10px;")
        unit_info.addWidget(name_label)

        species_label = QLabel(f"🏛️ {species}")
        species_color = "#ff6b6b" if area_type == "DUA" else "#696969"
        species_label.setStyleSheet(f"color: {species_color}; font-size: 9px;")
        unit_info.addWidget(species_label)

        layout.addLayout(unit_info)

        # Death info
        death_info = QVBoxLayout()

        # Death cause/time
        unit_data.get("death_cause", "Combat")
        turn_died = unit_data.get("turn_died", "?")
        death_label = QLabel(f"⚔️ T{turn_died}")
        death_label.setStyleSheet("color: #ddd; font-size: 9px;")
        death_info.addWidget(death_label)

        # Owner
        owner = unit_data.get("owner", "Unknown")
        owner_label = QLabel(f"👤 {owner}")
        owner_color = "#ff8b8b" if area_type == "DUA" else "#898989"
        owner_label.setStyleSheet(f"color: {owner_color}; font-size: 8px;")
        death_info.addWidget(owner_label)

        layout.addLayout(death_info)

    def mousePressEvent(self, event):  # noqa: N802
        """Handle mouse click to select unit."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.unit_selected.emit(self.unit_data)
        super().mousePressEvent(event)


class UnitAreasWidget(QWidget):
    """Combined widget displaying DUA and BUA for all players."""

    unit_selected = Signal(dict, str)  # unit_data, area_type
    refresh_requested = Signal()  # Emitted when refresh is requested
    resurrect_requested = Signal(dict)  # Emitted when resurrection is requested

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Tab widget for DUA and BUA
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #444;
                border-radius: 8px;
                background: #1a1a1a;
            }
            QTabBar::tab {
                background: #2f2f2f;
                color: white;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background: #4f4f4f;
                color: #ffd700;
            }
            QTabBar::tab:hover:!selected {
                background: #3f3f3f;
            }
        """)

        # DUA Tab
        self.dua_tab = self._create_area_tab("DUA", "💀 Dead Unit Area", "#8b0000", "#ff6b6b")
        self.tab_widget.addTab(self.dua_tab, "💀 DUA")

        # BUA Tab
        self.bua_tab = self._create_area_tab("BUA", "⚱️ Buried Unit Area", "#2f2f2f", "#696969")
        self.tab_widget.addTab(self.bua_tab, "⚱️ BUA")

        layout.addWidget(self.tab_widget)

    def _create_area_tab(self, area_type: str, title: str, bg_color: str, border_color: str) -> QWidget:
        """Create a tab for DUA or BUA."""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(8, 8, 8, 8)
        tab_layout.setSpacing(6)

        # Header with statistics and controls
        header_layout = QHBoxLayout()

        # Area statistics
        stats_label = QLabel(f"Units in {area_type}: 0")
        stats_label.setStyleSheet(f"""
            color: {border_color};
            font-size: 12px;
            font-weight: bold;
        """)
        header_layout.addWidget(stats_label)

        header_layout.addStretch()

        # Control buttons (only for DUA - resurrection)
        if area_type == "DUA":
            resurrect_btn = QPushButton("✨ Resurrect")
            resurrect_btn.setEnabled(False)
            resurrect_btn.setStyleSheet("""
                QPushButton {
                    background: #6b0000;
                    border: 1px solid #ff6b6b;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                    padding: 4px 8px;
                    font-size: 10px;
                }
                QPushButton:hover:enabled {
                    background: #8b0000;
                }
                QPushButton:pressed:enabled {
                    background: #4b0000;
                }
                QPushButton:disabled {
                    background: #444;
                    color: #888;
                    border-color: #666;
                }
            """)
            resurrect_btn.clicked.connect(lambda: self._handle_resurrect_clicked(area_type))
            header_layout.addWidget(resurrect_btn)

            # Store reference for enabling/disabling
            tab_widget.resurrect_btn = resurrect_btn

        refresh_btn = QPushButton("🔄")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-width: 25px;
                max-width: 25px;
                min-height: 20px;
                max-height: 20px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: #4f4f4f;
            }}
        """)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(refresh_btn)

        tab_layout.addLayout(header_layout)

        # Scrollable unit list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {bg_color};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {border_color};
                border-radius: 5px;
                min-height: 15px;
            }}
        """)

        # Container for unit items
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(3)

        # Empty state label
        empty_label = QLabel(f"No units in {area_type}")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet(f"""
            color: {border_color};
            font-style: italic;
            font-size: 11px;
            padding: 15px;
        """)
        content_layout.addWidget(empty_label)

        scroll_area.setWidget(content_widget)
        tab_layout.addWidget(scroll_area)

        # Store references for updates
        tab_widget.stats_label = stats_label
        tab_widget.content_layout = content_layout
        tab_widget.empty_label = empty_label
        tab_widget.selected_unit = None

        return tab_widget

    def update_dua_data(self, dua_data: Dict[str, List[Dict[str, Any]]]):
        """Update the DUA display with new data."""
        self._update_area_data(self.dua_tab, dua_data, "DUA")

    def update_bua_data(self, bua_data: Dict[str, List[Dict[str, Any]]]):
        """Update the BUA display with new data."""
        self._update_area_data(self.bua_tab, bua_data, "BUA")

    def _update_area_data(self, tab_widget: QWidget, data: Dict[str, List[Dict[str, Any]]], area_type: str):
        """Update area display with new data."""
        content_layout = tab_widget.content_layout
        stats_label = tab_widget.stats_label
        empty_label = tab_widget.empty_label

        # Clear existing content
        while content_layout.count() > 0:
            child = content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        total_units = 0

        # Group units by player
        for player_name, units in data.items():
            if not units:
                continue

            # Player section header
            player_header = QLabel(f"👤 {player_name}")
            player_header.setStyleSheet("""
                QLabel {
                    color: #ffd700;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 3px 6px;
                    background: rgba(0, 0, 0, 0.4);
                    border-radius: 3px;
                    margin: 3px 0px 1px 0px;
                }
            """)
            content_layout.addWidget(player_header)

            # Add units for this player
            for unit_data in units:
                unit_item = UnitAreaItem(unit_data, area_type)
                unit_item.unit_selected.connect(lambda ud, at=area_type: self._handle_unit_selected(ud, at, tab_widget))
                content_layout.addWidget(unit_item)
                total_units += 1

        # Update statistics
        stats_label.setText(f"Units in {area_type}: {total_units}")

        # Show empty state if no units
        if total_units == 0:
            content_layout.addWidget(empty_label)

        # Add stretch to push content to top
        content_layout.addStretch()

        # Reset selection
        tab_widget.selected_unit = None
        if hasattr(tab_widget, "resurrect_btn"):
            tab_widget.resurrect_btn.setEnabled(False)

    def _handle_unit_selected(self, unit_data: Dict[str, Any], area_type: str, tab_widget: QWidget):
        """Handle unit selection."""
        tab_widget.selected_unit = unit_data
        if area_type == "DUA" and hasattr(tab_widget, "resurrect_btn"):
            tab_widget.resurrect_btn.setEnabled(True)
        self.unit_selected.emit(unit_data, area_type)

    def _handle_resurrect_clicked(self, area_type: str):
        """Handle resurrect button click."""
        if area_type == "DUA":
            selected_unit = getattr(self.dua_tab, "selected_unit", None)
            if selected_unit:
                self.resurrect_requested.emit(selected_unit)

    def get_dua_count(self) -> int:
        """Get total number of units in DUA."""
        return self._get_area_count(self.dua_tab)

    def get_bua_count(self) -> int:
        """Get total number of units in BUA."""
        return self._get_area_count(self.bua_tab)

    def _get_area_count(self, tab_widget: QWidget) -> int:
        """Get number of units in an area."""
        content_layout = tab_widget.content_layout
        count = 0
        for i in range(content_layout.count()):
            widget = content_layout.itemAt(i).widget()
            if isinstance(widget, UnitAreaItem):
                count += 1
        return count
