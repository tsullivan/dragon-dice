# components/army_die_face_summary_widget.py
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import List, Dict, Optional
from collections import Counter
import constants
from models.unit_model import UnitModel
from models.unit_roster_model import UnitRosterModel


class ArmyDieFaceSummaryWidget(QWidget):
    """
    A compact widget that shows a summary of die faces for all units in an army.
    Displays counts of different face types (MELEE, MISSILE, MAGIC, etc.).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_roster: Optional[UnitRosterModel] = None
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(8)

        # Title
        title_label = QLabel("Die Summary:")
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(8)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Container for face counts
        self.summary_frame = QFrame()
        self.summary_layout = QHBoxLayout(self.summary_frame)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)
        self.summary_layout.setSpacing(5)
        layout.addWidget(self.summary_frame)

        layout.addStretch()  # Push everything to the left

        # Initialize with empty state
        self._show_empty_state()

    def _show_empty_state(self):
        """Show the widget in an empty state."""
        self._clear_summary()
        empty_label = QLabel("—")
        empty_label.setStyleSheet("color: #999; font-style: italic;")
        self.summary_layout.addWidget(empty_label)

    def _clear_summary(self):
        """Clear all existing summary labels."""
        while self.summary_layout.count():
            child = self.summary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _get_icon_for_face(self, face_type: str) -> str:
        """Get display icon for a die face type."""
        icon_map = {
            constants.ICON_MELEE: "⚔️",
            constants.ICON_MISSILE: "🏹",
            constants.ICON_MAGIC: "✨",
            constants.ICON_SAVE: "🛡️",
            constants.ICON_MANEUVER: "🏃",
            constants.ICON_SAI: "💎",
        }
        return icon_map.get(face_type, "❓")

    def _count_die_faces(self, units: List[UnitModel]) -> Dict[str, int]:
        """Count all die faces from a list of units."""
        if not self.unit_roster or not units:
            return {}

        face_counts = Counter()

        for unit in units:
            unit_def = self.unit_roster.get_unit_definition(unit.unit_type)
            if not unit_def:
                continue

            die_faces = unit_def.get("die_faces", {})

            # Count standard faces (face_1 through face_6)
            for face_key in [
                "face_1",
                "face_2",
                "face_3",
                "face_4",
                "face_5",
                "face_6",
            ]:
                face_type = die_faces.get(face_key)
                if face_type and face_type != "ID":  # Don't count ID faces
                    face_counts[face_type] += 1

            # Count eighth faces
            for face_key in ["eighth_face_1", "eighth_face_2"]:
                face_type = die_faces.get(face_key)
                if face_type and face_type != "ID":  # Don't count ID faces
                    face_counts[face_type] += 1

        return dict(face_counts)

    def set_units_and_roster(
        self, units: List[UnitModel], unit_roster: UnitRosterModel
    ):
        """Update the summary with new units and roster."""
        self.unit_roster = unit_roster

        if not units:
            self._show_empty_state()
            return

        self._clear_summary()

        face_counts = self._count_die_faces(units)

        if not face_counts:
            self._show_empty_state()
            return

        # Show the most common face types in a compact format
        priority_order = [
            constants.ICON_MELEE,
            constants.ICON_MISSILE,
            constants.ICON_MAGIC,
            constants.ICON_SAVE,
            constants.ICON_MANEUVER,
            constants.ICON_SAI,
        ]

        # Sort by priority, then by count (descending)
        sorted_faces = sorted(
            face_counts.items(),
            key=lambda x: (
                priority_order.index(x[0]) if x[0] in priority_order else 999,
                -x[1],
            ),
        )

        for face_type, count in sorted_faces:
            icon = self._get_icon_for_face(face_type)
            face_label = QLabel(f"{icon}{count}")
            face_label.setToolTip(f"{face_type}: {count} faces")
            face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            face_label.setStyleSheet(
                "padding: 2px 4px; "
                "border: 1px solid #ddd; "
                "border-radius: 3px; "
                "background-color: #f8f8f8; "
                "font-size: 10px;"
            )
            self.summary_layout.addWidget(face_label)

    def clear(self):
        """Clear the die face summary."""
        self.unit_roster = None
        self._show_empty_state()
