# components/die_face_display_widget.py
from typing import List, Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


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
            label.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd; color: #999;")

    def _get_face_display_info(self, face_name: str, face_description: str) -> Tuple[str, str, str]:
        """Get display information for a die face.

        Returns:
            tuple: (display_text, background_color, tooltip)
        """
        if not face_name:
            return "?", "#f0f0f0", "Unknown face type"

        # Import UnitFace here to avoid circular imports
        from models.unit_model import UnitFace

        # Create a temporary UnitFace to get display info
        temp_face = UnitFace(face_name, face_description)
        return temp_face.get_display_info()

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
            face_label.setMinimumSize(60, 50)  # Larger for emoji + text
            face_label.setFrameStyle(QFrame.Shape.Box)
            face_label.setStyleSheet(
                "background-color: #f0f0f0; border: 1px solid #ccc; font-size: 9px; text-align: center; padding: 2px;"
            )

            row = i // cols
            col = i % cols
            self.faces_layout.addWidget(face_label, row, col)
            self.face_labels.append(face_label)

    def set_die_faces(self, unit_faces: Optional[List], is_monster: bool = False):
        """Set the die face data to display.

        Args:
            unit_faces: List of UnitFace objects with name and description
            is_monster: Whether this unit is a monster (affects display layout)
        """
        self.die_face_data = unit_faces
        self.is_monster = is_monster

        if not unit_faces:
            self._show_empty_state()
            return

        # Create appropriate number of labels
        num_faces = len(unit_faces)
        self._create_face_labels(num_faces)

        # Update each face label
        for i, face in enumerate(unit_faces):
            if i < len(self.face_labels):
                label = self.face_labels[i]

                # Use the face's built-in display methods if it's a UnitFace object
                if hasattr(face, "get_display_info"):
                    display_text, background_color, tooltip = face.get_display_info()
                else:
                    # Fallback for legacy face data
                    display_text, background_color, tooltip = self._get_face_display_info(face.name, face.description)

                label.setText(display_text)
                label.setStyleSheet(
                    f"background-color: {background_color}; border: 1px solid #ccc; "
                    f"font-size: 9px; text-align: center; padding: 3px; line-height: 1.2;"
                )
                label.setToolTip(tooltip)

    def clear(self):
        """Clear the die face display."""
        self.set_die_faces(None, False)
