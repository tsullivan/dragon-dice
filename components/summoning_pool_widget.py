"""
Summoning Pool Widget for Dragon Dice.

This widget displays the summoning pool contents for all players,
showing available dragons with their elements, health, and ownership.
Based on the design from assets/playmat.html.
"""

from typing import Any, Dict, List

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


class DragonDisplayItem(QFrame):
    """Individual dragon display item with element icons and health."""

    dragon_selected = Signal(dict)  # Emit dragon data when clicked

    def __init__(self, dragon_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.dragon_data = dragon_data
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)

        # Apply styling similar to playmat
        self.setStyleSheet("""
            DragonDisplayItem {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4b0082, stop:1 #2a004a);
                border: 2px solid #dda0dd;
                border-radius: 8px;
                margin: 2px;
            }
            DragonDisplayItem:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6a00a2, stop:1 #4a006a);
                border-color: #ffa0ff;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Dragon type and form
        dragon_info = QVBoxLayout()

        # Dragon name/type
        dragon_type = dragon_data.get("dragon_type", "Unknown")
        dragon_form = dragon_data.get("dragon_form", "Dragon")
        name_label = QLabel(f"🐲 {dragon_type} {dragon_form}")
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        dragon_info.addWidget(name_label)

        # Elements display
        elements = dragon_data.get("elements", [])
        if elements:
            elements_text = " ".join([self._get_element_icon(elem) for elem in elements])
            elements_label = QLabel(elements_text)
            elements_label.setStyleSheet("color: #dda0dd; font-size: 14px;")
            dragon_info.addWidget(elements_label)

        layout.addLayout(dragon_info)

        # Health and owner info
        info_layout = QVBoxLayout()

        # Health
        health = dragon_data.get("health", 0)
        health_label = QLabel(f"❤️ {health}")
        health_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        info_layout.addWidget(health_label)

        # Owner
        owner = dragon_data.get("owner", "Unknown")
        owner_label = QLabel(f"👤 {owner}")
        owner_label.setStyleSheet("color: #90ee90; font-size: 10px;")
        info_layout.addWidget(owner_label)

        layout.addLayout(info_layout)

        # Location (if summoned)
        location = dragon_data.get("location")
        if location:
            location_label = QLabel(f"📍 {location}")
            location_label.setStyleSheet("color: #ffd700; font-size: 10px;")
            info_layout.addWidget(location_label)

    def _get_element_icon(self, element: str) -> str:
        """Get icon for dragon element."""
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

    def mousePressEvent(self, event):  # noqa: N802
        """Handle mouse click to select dragon."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragon_selected.emit(self.dragon_data)
        super().mousePressEvent(event)


class SummoningPoolWidget(QGroupBox):
    """Widget displaying summoning pool contents for all players."""

    dragon_selected = Signal(dict)  # Emitted when a dragon is selected
    refresh_requested = Signal()  # Emitted when refresh is requested

    def __init__(self, parent=None):
        super().__init__("🔮 Summoning Pool", parent)
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)

        # Apply playmat-inspired styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: white;
                border: 3px solid #dda0dd;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #9370db, stop:1 #4b0082);
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

        # Header with refresh button
        header_layout = QHBoxLayout()

        # Pool statistics
        self.stats_label = QLabel("Dragons Available: 0")
        self.stats_label.setStyleSheet("""
            color: #dda0dd;
            font-size: 12px;
            font-weight: normal;
        """)
        header_layout.addWidget(self.stats_label)

        header_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #6a00a2;
                border: 1px solid #dda0dd;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-width: 30px;
                max-width: 30px;
                min-height: 25px;
                max-height: 25px;
            }
            QPushButton:hover {
                background: #8a00c2;
            }
            QPushButton:pressed {
                background: #4a0082;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Scrollable dragon list
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
                background: #2a004a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #dda0dd;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ffa0ff;
            }
        """)

        # Container for dragon items
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)

        # Empty state label
        self.empty_label = QLabel("No dragons in summoning pool")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            color: #dda0dd;
            font-style: italic;
            font-size: 12px;
            padding: 20px;
        """)
        self.content_layout.addWidget(self.empty_label)

        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)

    def update_pool_data(self, pool_data: Dict[str, List[Dict[str, Any]]]):
        """Update the summoning pool display with new data.

        Args:
            pool_data: Dictionary mapping player names to their dragon lists
        """
        # Clear existing content
        while self.content_layout.count() > 0:
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        total_dragons = 0

        # Group dragons by player
        for player_name, dragons in pool_data.items():
            if not dragons:
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

            # Add dragons for this player
            for dragon_data in dragons:
                dragon_item = DragonDisplayItem(dragon_data)
                dragon_item.dragon_selected.connect(self.dragon_selected.emit)
                self.content_layout.addWidget(dragon_item)
                total_dragons += 1

        # Update statistics
        self.stats_label.setText(f"Dragons Available: {total_dragons}")

        # Show empty state if no dragons
        if total_dragons == 0:
            self.content_layout.addWidget(self.empty_label)

        # Add stretch to push content to top
        self.content_layout.addStretch()

    def highlight_player_dragons(self, player_name: str):
        """Highlight dragons belonging to a specific player."""
        # This could be implemented to show visual emphasis
        # for the current player's dragons
        pass

    def get_dragon_count(self) -> int:
        """Get total number of dragons in the pool."""
        count = 0
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if isinstance(widget, DragonDisplayItem):
                count += 1
        return count
