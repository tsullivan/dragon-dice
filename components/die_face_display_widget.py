# components/die_face_display_widget.py
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Dict, Optional
import constants


class DieFaceDisplayWidget(QWidget):
    """
    A widget that displays the die faces for a Dragon Dice unit.
    Shows the 6 standard faces plus 2 eighth faces with appropriate icons.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.die_face_data: Optional[Dict[str, str]] = None
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title
        title_label = QLabel("Die Faces")
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Standard faces (1-6) in a 2x3 grid
        standard_frame = QFrame()
        standard_frame.setFrameStyle(QFrame.Shape.Box)
        standard_layout = QGridLayout(standard_frame)
        standard_layout.setContentsMargins(5, 5, 5, 5)
        standard_layout.setSpacing(3)

        self.standard_face_labels = {}
        for i in range(1, 7):
            face_label = QLabel("?")
            face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            face_label.setMinimumSize(30, 30)
            face_label.setFrameStyle(QFrame.Shape.Box)
            face_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
            
            row = (i - 1) // 3
            col = (i - 1) % 3
            standard_layout.addWidget(face_label, row, col)
            self.standard_face_labels[f"face_{i}"] = face_label

        layout.addWidget(standard_frame)

        # Eighth faces
        eighth_frame = QFrame()
        eighth_frame.setFrameStyle(QFrame.Shape.Box)
        eighth_layout = QHBoxLayout(eighth_frame)
        eighth_layout.setContentsMargins(5, 5, 5, 5)
        eighth_layout.setSpacing(10)

        eighth_title = QLabel("8th Faces:")
        eighth_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        eighth_layout.addWidget(eighth_title)

        self.eighth_face_labels = {}
        for i in range(1, 3):
            face_label = QLabel("?")
            face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            face_label.setMinimumSize(30, 30)
            face_label.setFrameStyle(QFrame.Shape.Box)
            face_label.setStyleSheet("background-color: #ffe6e6; border: 1px solid #ffcccc;")
            
            eighth_layout.addWidget(face_label)
            self.eighth_face_labels[f"eighth_face_{i}"] = face_label

        layout.addWidget(eighth_frame)

        # Initially show empty state
        self._show_empty_state()

    def _show_empty_state(self):
        """Show the widget in an empty state."""
        for label in self.standard_face_labels.values():
            label.setText("—")
            label.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd; color: #999;")
        
        for label in self.eighth_face_labels.values():
            label.setText("—")
            label.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd; color: #999;")

    def _get_icon_for_face(self, face_type: str) -> str:
        """Get display icon/text for a die face type."""
        icon_map = {
            constants.ICON_MELEE: "⚔️",
            constants.ICON_MISSILE: "🏹", 
            constants.ICON_MAGIC: "✨",
            constants.ICON_SAVE: "🛡️",
            constants.ICON_ID: "—",
            constants.ICON_SAI: "💎",
            constants.ICON_MANEUVER: "🏃",
            constants.ICON_DRAGON_ATTACK_CLAW: "🗺️",
            constants.ICON_DRAGON_ATTACK_BITE: "🦷",
            constants.ICON_DRAGON_ATTACK_TAIL: "🐉",
            constants.ICON_DRAGON_BREATH: "🔥",
        }
        return icon_map.get(face_type, "❓")

    def _get_color_for_face(self, face_type: str) -> str:
        """Get background color for a die face type."""
        color_map = {
            constants.ICON_MELEE: "#ffeeee",      # Light red
            constants.ICON_MISSILE: "#eeeeff",    # Light blue
            constants.ICON_MAGIC: "#ffffee",      # Light yellow
            constants.ICON_SAVE: "#eeffee",       # Light green
            constants.ICON_ID: "#f0f0f0",         # Light gray
            constants.ICON_SAI: "#ffeeff",        # Light purple
            constants.ICON_MANEUVER: "#eeffff",   # Light cyan
        }
        return color_map.get(face_type, "#f0f0f0")

    def set_die_faces(self, die_face_data: Optional[Dict[str, str]]):
        """Set the die face data to display."""
        self.die_face_data = die_face_data
        
        if not die_face_data:
            self._show_empty_state()
            return

        # Update standard faces
        for face_key, label in self.standard_face_labels.items():
            face_type = die_face_data.get(face_key, "ID")
            icon = self._get_icon_for_face(face_type)
            color = self._get_color_for_face(face_type)
            
            label.setText(icon)
            label.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc;")
            label.setToolTip(f"{face_key.replace('_', ' ').title()}: {face_type}")

        # Update eighth faces
        for face_key, label in self.eighth_face_labels.items():
            face_type = die_face_data.get(face_key, "ID")
            icon = self._get_icon_for_face(face_type)
            color = self._get_color_for_face(face_type)
            
            label.setText(icon)
            label.setStyleSheet(f"background-color: {color}; border: 1px solid #ffcccc;")
            label.setToolTip(f"{face_key.replace('_', ' ').title()}: {face_type}")

    def clear(self):
        """Clear the die face display."""
        self.set_die_faces(None)