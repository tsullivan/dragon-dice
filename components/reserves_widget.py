"""
Reserves Widget for Dragon Dice.

This widget displays reserve units for all players, showing available
units for deployment with their health, species, and elements.
Based on the design from assets/playmat.html.
"""

from typing import Any, Dict, List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QFrame,
    QPushButton,
    QGridLayout,
)
from PySide6.QtGui import QFont, QPalette


class ReserveUnitItem(QFrame):
    """Individual reserve unit display item."""

    unit_selected = Signal(dict)  # Emit unit data when clicked

    def __init__(self, unit_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.unit_data = unit_data
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        self.setMinimumHeight(50)
        self.setMaximumHeight(70)

        # Apply green gradient styling from playmat
        self.setStyleSheet("""
            ReserveUnitItem {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #228b22, stop:1 #006400);
                border: 2px solid #90ee90;
                border-radius: 8px;
                margin: 2px;
            }
            ReserveUnitItem:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #32ab32, stop:1 #008400);
                border-color: #b0ffb0;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Unit info
        unit_info = QVBoxLayout()

        # Unit name and species
        name = unit_data.get("name", "Unknown Unit")
        species = unit_data.get("species", "Unknown")
        name_label = QLabel(f"⚔️ {name}")
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        unit_info.addWidget(name_label)

        species_label = QLabel(f"🏛️ {species}")
        species_label.setStyleSheet("color: #90ee90; font-size: 10px;")
        unit_info.addWidget(species_label)

        layout.addLayout(unit_info)

        # Health and elements
        stats_layout = QVBoxLayout()

        # Health
        health = unit_data.get("health", 0)
        max_health = unit_data.get("max_health", health)
        health_label = QLabel(f"❤️ {health}/{max_health}")
        health_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 10px;")
        stats_layout.addWidget(health_label)

        # Elements
        elements = unit_data.get("elements", [])
        if elements:
            elements_text = " ".join([self._get_element_icon(elem) for elem in elements])
            elements_label = QLabel(elements_text)
            elements_label.setStyleSheet("color: #ffd700; font-size: 12px;")
            stats_layout.addWidget(elements_label)

        layout.addLayout(stats_layout)

        # Reserve info
        reserve_info = QVBoxLayout()

        # Turns in reserves
        turns_in_reserves = unit_data.get("turns_in_reserves", 0)
        if turns_in_reserves > 0:
            turns_label = QLabel(f"⏰ {turns_in_reserves}")
            turns_label.setStyleSheet("color: #ddd; font-size: 9px;")
            reserve_info.addWidget(turns_label)

        # Owner
        owner = unit_data.get("owner", "Unknown")
        owner_label = QLabel(f"👤 {owner}")
        owner_label.setStyleSheet("color: #b0ffb0; font-size: 9px;")
        reserve_info.addWidget(owner_label)

        layout.addLayout(reserve_info)

    def _get_element_icon(self, element: str) -> str:
        """Get icon for unit element."""
        icons = {
            "air": "💨",
            "death": "💀",
            "earth": "🌍",
            "fire": "🔥",
            "water": "💧",
            "ivory": "🤍",
            "white": "⚪",
        }
        return icons.get(element.lower(), "❓")

    def mousePressEvent(self, event):
        """Handle mouse click to select unit."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.unit_selected.emit(self.unit_data)
        super().mousePressEvent(event)


class ReservesWidget(QGroupBox):
    """Widget displaying reserve units for all players."""

    unit_selected = Signal(dict)  # Emitted when a unit is selected
    refresh_requested = Signal()  # Emitted when refresh is requested
    deploy_requested = Signal(dict)  # Emitted when deployment is requested

    def __init__(self, parent=None):
        super().__init__("🏰 Reserve Area", parent)
        self.setMinimumWidth(300)
        self.setMinimumHeight(250)

        # Apply green gradient styling from playmat
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: white;
                border: 3px solid #90ee90;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #228b22, stop:1 #006400);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #ffd700;
                font-size: 16px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(8)

        # Header with statistics and controls
        header_layout = QHBoxLayout()

        # Reserve statistics
        self.stats_label = QLabel("Units in Reserves: 0")
        self.stats_label.setStyleSheet("""
            color: #90ee90; 
            font-size: 12px; 
            font-weight: normal;
        """)
        header_layout.addWidget(self.stats_label)

        header_layout.addStretch()

        # Control buttons
        self.deploy_btn = QPushButton("🚀 Deploy")
        self.deploy_btn.setEnabled(False)
        self.deploy_btn.setStyleSheet("""
            QPushButton {
                background: #32ab32;
                border: 1px solid #90ee90;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover:enabled {
                background: #52cb52;
            }
            QPushButton:pressed:enabled {
                background: #12ab12;
            }
            QPushButton:disabled {
                background: #444;
                color: #888;
                border-color: #666;
            }
        """)
        self.deploy_btn.clicked.connect(self._handle_deploy_clicked)
        header_layout.addWidget(self.deploy_btn)

        refresh_btn = QPushButton("🔄")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #32ab32;
                border: 1px solid #90ee90;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-width: 30px;
                max-width: 30px;
                min-height: 25px;
                max-height: 25px;
            }
            QPushButton:hover {
                background: #52cb52;
            }
            QPushButton:pressed {
                background: #12ab12;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Scrollable unit list
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
                background: #004400;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #90ee90;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #b0ffb0;
            }
        """)

        # Container for unit items
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)

        # Empty state label
        self.empty_label = QLabel("No units in reserves")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            color: #90ee90;
            font-style: italic;
            font-size: 12px;
            padding: 20px;
        """)
        self.content_layout.addWidget(self.empty_label)

        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)

        # Track selected unit
        self.selected_unit = None

    def update_reserves_data(self, reserves_data: Dict[str, List[Dict[str, Any]]]):
        """Update the reserves display with new data.

        Args:
            reserves_data: Dictionary mapping player names to their reserve unit lists
        """
        # Clear existing content
        while self.content_layout.count() > 0:
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        total_units = 0

        # Group units by player
        for player_name, units in reserves_data.items():
            if not units:
                continue

            # Player section header
            player_header = QLabel(f"👤 {player_name}")
            player_header.setStyleSheet("""
                QLabel {
                    color: #ffd700;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 4px 8px;
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 4px;
                    margin: 4px 0px 2px 0px;
                }
            """)
            self.content_layout.addWidget(player_header)

            # Add units for this player
            for unit_data in units:
                unit_item = ReserveUnitItem(unit_data)
                unit_item.unit_selected.connect(self._handle_unit_selected)
                self.content_layout.addWidget(unit_item)
                total_units += 1

        # Update statistics
        self.stats_label.setText(f"Units in Reserves: {total_units}")

        # Show empty state if no units
        if total_units == 0:
            self.content_layout.addWidget(self.empty_label)

        # Add stretch to push content to top
        self.content_layout.addStretch()

        # Reset selection
        self.selected_unit = None
        self.deploy_btn.setEnabled(False)

    def _handle_unit_selected(self, unit_data: Dict[str, Any]):
        """Handle unit selection."""
        self.selected_unit = unit_data
        self.deploy_btn.setEnabled(True)
        self.unit_selected.emit(unit_data)

    def _handle_deploy_clicked(self):
        """Handle deploy button click."""
        if self.selected_unit:
            self.deploy_requested.emit(self.selected_unit)

    def highlight_player_units(self, player_name: str):
        """Highlight units belonging to a specific player."""
        # This could be implemented to show visual emphasis
        # for the current player's units
        pass

    def get_unit_count(self) -> int:
        """Get total number of units in reserves."""
        count = 0
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if isinstance(widget, ReserveUnitItem):
                count += 1
        return count

    def get_player_unit_count(self, player_name: str) -> int:
        """Get number of units in reserves for a specific player."""
        # This would need to track player ownership in the items
        # For now, return 0 as placeholder
        return 0
