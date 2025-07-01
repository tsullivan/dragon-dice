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

from typing import Dict, Optional, List
import utils.constants as constants
from models.die_face_model import DIE_FACES_DATA


class DieFaceDisplayWidget(QWidget):
    """
    A widget that displays the die faces for a Dragon Dice unit.
    Shows 6 faces for regular units, 10 faces for monsters with appropriate icons and values.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.die_face_data: Optional[List[str]] = None
        self.is_monster = False
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

        # Die faces in a grid layout (2x3 for regular units, 2x5 for monsters)
        self.faces_frame = QFrame()
        self.faces_frame.setFrameStyle(QFrame.Shape.Box)
        self.faces_layout = QGridLayout(self.faces_frame)
        self.faces_layout.setContentsMargins(5, 5, 5, 5)
        self.faces_layout.setSpacing(3)

        # Will be populated dynamically based on unit type
        self.face_labels = []

        layout.addWidget(self.faces_frame)

        # Initially show empty state
        self._show_empty_state()

    def _show_empty_state(self):
        """Show the widget in an empty state."""
        for label in self.face_labels:
            label.setText("—")
            label.setStyleSheet(
                "background-color: #f8f8f8; border: 1px solid #ddd; color: #999;"
            )

    def _get_face_display_info(self, face_key: str) -> tuple[str, str, str]:
        """Get display information for a die face key.

        Returns:
            tuple: (display_text, background_color, tooltip)
        """
        if not face_key or face_key not in DIE_FACES_DATA:
            return "?", "#f0f0f0", "Unknown face type"

        face_model = DIE_FACES_DATA[face_key]

        # Create display text with face type and value
        if face_model.value:
            display_text = (
                f"{face_model.icon}\n{face_model.face_type}_{face_model.value}"
            )
        else:
            display_text = f"{face_model.icon}\n{face_model.face_type}"

        # Get background color based on face type
        color_map = {
            "MELEE": "#ffeeee",  # Light red
            "MISSILE": "#eeeeff",  # Light blue
            "MAGIC": "#ffffee",  # Light yellow
            "SAVE": "#eeffee",  # Light green
            "ID": "#f0f0f0",  # Light gray
            "MOVE": "#fff0ee",  # Light orange
            "JAWS": "#ffe0e0",  # Dragon red
            "CLAW": "#e0e0ff",  # Dragon blue
            "BELLY": "#e0ffe0",  # Dragon green
            "TAIL": "#ffffe0",  # Dragon yellow
            "TREASURE": "#ffe0ff",  # Dragon purple
        }
        background_color = color_map.get(face_model.face_type, "#f0f0f0")

        # Create tooltip
        tooltip = f"{face_model.display_name}: {face_model.description}"

        return display_text, background_color, tooltip

    def _clear_faces_layout(self):
        """Clear all face labels from the layout."""
        for label in self.face_labels:
            self.faces_layout.removeWidget(label)
            label.deleteLater()
        self.face_labels.clear()

    def _create_face_labels(self, num_faces: int):
        """Create face labels for the specified number of faces."""
        self._clear_faces_layout()

        # Determine grid layout based on face count
        if num_faces <= 6:
            # Regular units: 2 rows, 3 columns
            rows, cols = 2, 3
        else:
            # Monsters: 2 rows, 5 columns
            rows, cols = 2, 5

        for i in range(num_faces):
            face_label = QLabel("?")
            face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            face_label.setMinimumSize(50, 40)  # Larger for better readability
            face_label.setFrameStyle(QFrame.Shape.Box)
            face_label.setStyleSheet(
                "background-color: #f0f0f0; border: 1px solid #ccc; font-size: 8px; text-align: center;"
            )

            row = i // cols
            col = i % cols
            self.faces_layout.addWidget(face_label, row, col)
            self.face_labels.append(face_label)

    def set_die_faces(
        self, die_face_data: Optional[List[str]], is_monster: bool = False
    ):
        """Set the die face data to display.

        Args:
            die_face_data: List of face keys (e.g., ['ID_1', 'MELEE_2', ...])
            is_monster: Whether this unit is a monster (affects display layout)
        """
        self.die_face_data = die_face_data
        self.is_monster = is_monster

        if not die_face_data:
            self._show_empty_state()
            return

        # Create appropriate number of labels
        num_faces = len(die_face_data)
        self._create_face_labels(num_faces)

        # Update each face label
        for i, face_key in enumerate(die_face_data):
            if i < len(self.face_labels):
                label = self.face_labels[i]
                display_text, background_color, tooltip = self._get_face_display_info(
                    face_key
                )

                label.setText(display_text)
                label.setStyleSheet(
                    f"background-color: {background_color}; border: 1px solid #ccc; "
                    f"font-size: 8px; text-align: center; padding: 2px;"
                )
                label.setToolTip(tooltip)

    def clear(self):
        """Clear the die face display."""
        self.set_die_faces(None, False)
